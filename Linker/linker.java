import java.util.*;
import java.lang.*;

/**
 * This is the program file for the linker project.
 * Error and warning checking mechanism are included in the program and have
 * been merged within actions immediately after each passes.
 * The details of the linker program can be found in specification for this lab.
 *
 * @author: Jiaqi Liu
 * @version:09/17/2018 (last modification)
 */

public class linker{
  public static final int MAX_PHYSICAL_ADDRESS = 299;

  /** the main func interacts with the user and provides guidance
  * It receives data through standard input (keyboard).
  *
  * Please note that the program outputs the symbol table on the console
  * immediately after the completion of pass one.
  *
  * @return (display on console) the symbol table, memory map, and possibly
  * some errors and warning messages if detected.
  *
  * @throws no exception
  */
  public static void main(String agrs[]){
    System.out.println("Pass one begin");
    HashMap<String, Integer> dict = getSymbolDict();
    outputSymbolTable(dict);
    System.out.println("Pass two begin");
    ArrayList<Integer> address = calcAddress(dict);
    outputAddress(address);
  }

  // display memory address to the console
  public static void outputAddress(ArrayList<Integer> lst){
    System.out.printf("Memory Map\n");
    for(int i=0;i<lst.size();++i){
      System.out.printf("%d:\t%d\n",i,lst.get(i));
    }
    System.out.printf("\n");
  }

  // print the symbol table on the console in sorted order
  public static void outputSymbolTable(HashMap<String,Integer> d){
    System.out.println("\n\nSymbol Table");
    Object[] symbol_arr = d.keySet().toArray();
    Arrays.sort(symbol_arr);
    for(Object symbol:symbol_arr){
      int correspondence_address = d.get(symbol);
      System.out.println(symbol + "=" + correspondence_address);
    }
    System.out.println();
  }

  // determines whehter a string can be converted to a number (integer)
  public static boolean isNumber(String s){
    // determine whether a string can parse to an interger
    try{
      Integer.parseInt(s);
    }
    catch(NumberFormatException notNumber){
      return false;
    }
    return true;
  }

  // display error message from a message list
  public static void dispErrMsg(ArrayList<String> lst){

    // remove identical warning and error messages
    Set<String> hash_set = new HashSet<>();
    hash_set.addAll(lst);
    lst.clear();
    lst.addAll(hash_set);
    System.out.printf("\n");
    // display warning and error message
    for(int i=0;i<lst.size();++i){
      System.out.println(lst.get(i));
    }
    System.out.printf("\n");
  }

  // the function eliminates irrelavant informations such as space, tabs, etc.
  public static List<String> purifyInput(String s){
    // tokens are not exactly seperated by one space, thus are not clean
    String unclean_token[] = s.split(" ");
    List<String> token = new ArrayList<String>(Arrays.asList(unclean_token));
    // removes all the empty strings in the list to purify the token list
    token.removeAll(Arrays.asList("",null,"\t"));
    return token;
  }

  // it gets a string that contains the symbol and the current base address
  // returns an Symbol dictionary HashMap that contains symbol and address
  public static HashMap<String,Integer> getSymbolDict(){
    // a key-value dictionary mapping symbols to their absolute addresses
    HashMap<String, Integer> dict = new HashMap<String, Integer>();
    // signal flag for whether prompt for more inputs
    boolean ask_for_input = true;
    // initialize a Scanner object for standard input
    Scanner in = new Scanner(System.in);
    // book keeping current module's base address
    int base_address = 0;
    // signal flag for whether the module number have been received
    boolean read_module_number = false;
    // stores in a format of key, value, key, value ...
    ArrayList<Object> key_val_lst = new ArrayList<>();

    // declare definition list flags for complete status
    boolean def_lst_comp = true;
    // flag for whether received the number of definitions
    boolean get_num_of_defs = false;
    int num_of_defs = 0;
    int remaining_def_elem = 0;

    int pair_in_cur_module = 0;
    ArrayList<String> err_msg = new ArrayList<>();

    // declare use list flags for complete status
    boolean use_lst_comp = true;
    boolean get_num_of_use_types = false;
    int remaining_use_types = 0;

    // declare base address flags for complete status
    boolean base_comp = true;
    boolean get_module_len = false;
    int module_len = 0;
    // book keeping remaining modules
    int module_number=Integer.MIN_VALUE;

    while (ask_for_input){
      String input = in.nextLine();

      // the user have not yet complete all the inputs

      List<String> token = purifyInput(input);

      for(int i=0;i<token.size();++i){
        // the first valid input number would always be module number
        if(!read_module_number && isNumber(token.get(i))){
          read_module_number = true;
          module_number = Integer.parseInt(token.get(i));
          continue;
        }
        else if(def_lst_comp && use_lst_comp && base_comp){
          // start analyze definition list
          def_lst_comp = false;
        }
        // begin analyzing definition list
        if (!def_lst_comp){
          if (!get_num_of_defs){
            pair_in_cur_module = Integer.parseInt(token.get(i));
            remaining_def_elem = 2 * pair_in_cur_module;

            get_num_of_defs = true;
            if (remaining_def_elem == 0){
              def_lst_comp = true;
              get_num_of_defs = false;
              // switch to use list analysis
              use_lst_comp = false;
            }
          }
          else if(get_num_of_defs && remaining_def_elem!=0){
            if(isNumber(token.get(i))){
              // calc abs address by adding relative address to base address
              int abs_address = Integer.parseInt(token.get(i)) + base_address;
              key_val_lst.add(abs_address);
            }
            else{
              key_val_lst.add(token.get(i));
            }
            --remaining_def_elem;
            if(remaining_def_elem==0){
              def_lst_comp = true;
              get_num_of_defs = false;
              // switch to use list analysis
              use_lst_comp = false;
            }
          }
        }
        // begin analyzing use list
        else if(!use_lst_comp){
          // the number of use type instructions has not been received
          if (!get_num_of_use_types){
            remaining_use_types = Integer.parseInt(token.get(i));
            get_num_of_use_types = true;
            if(remaining_use_types==0){
              get_num_of_use_types = false;
              use_lst_comp = true;
              // switch to base address analysis
              base_comp = false;
            }
          }
          // the number of use type instructions has been receeived
          else{
            if(isNumber(token.get(i)) && remaining_use_types!=0){
              if(Integer.parseInt(token.get(i)) == -1){
                --remaining_use_types;
                if(remaining_use_types == 0){
                  get_num_of_use_types = false;
                  use_lst_comp = true;
                  // switch to base address analysis
                  base_comp = false;
                }
              }
            }
          }
        }
        // begin analyzing base addresses
        else if(!base_comp){
          if(!get_module_len){
            module_len = Integer.parseInt(token.get(i));
            // Error checking: no definition should exceed the size of cur module
            // check current module backwards from the key_val_lst
            int cursor = key_val_lst.size()-1;
            for(int j=0;j<pair_in_cur_module;++j){
              if ( ((Integer)key_val_lst.get(cursor))-base_address >= module_len){
                key_val_lst.set(cursor,module_len-1+base_address);
                err_msg.add("Error: The symbol: "+ key_val_lst.get(cursor-1)+" exceeded the size of current module; last word in module used.");
              }
              // update the cursor by factor of 2 to skip key
              cursor-=2*j;
            }

            get_module_len = true;
            // update base address based on the current module length
            base_address += module_len;
            if(module_len == 0){
              get_module_len = false;
              base_comp = true;
            }
          }
          else{
            --module_len;
            if (module_len == 0){
              get_module_len = false;
              base_comp = true;
              // update remaining module numbers
              --module_number;
              // the user have completed the first pass
              if(module_number==0)
                ask_for_input = false; // no further input needed
            }
          }
        }
      }

    }
    // in.close(); avoid closing the standard system input stream

    // extracting and grouping information for mapping
    for(int i=0;i<key_val_lst.size();i+=2){
      String symbol = (String) key_val_lst.get(i);
      int correspondence_address = (Integer) key_val_lst.get(i+1);
      // error checking: no symbol should not defined more than once
      if(dict.containsKey(symbol)){
        err_msg.add("Error: The symbol "+symbol+" is multiply defined; last value used.");
      }
      dict.put(symbol,correspondence_address);
    }
    dispErrMsg(err_msg);
    return dict;
  }

  // the function calculates the absolute (final) address after linking through
  // resolving external reference and relocate relative address
  // the output is an new entry (instruction) ArrayList after linking
  public static ArrayList<Integer> calcAddress(HashMap<String,Integer> dict){
    // initialize a Scanner object for standard input
    Scanner in = new Scanner(System.in);
    boolean ask_for_input = true;

    // book keeping current module's base address
    int base_address = 0;
    // signal flag for whether the module number have been received
    boolean read_module_number = false;

    // record absolute index for index that have been used as a symbol
    // specifically use for a predefined error case
    ArrayList<Integer> remove_lst = new ArrayList<Integer>();

    // declare definition list flags for complete status
    boolean def_lst_comp = true;
    // flag for whether received the number of definitions
    boolean get_num_of_defs = false;
    int num_of_defs = 0;
    int remaining_def_elem = 0;

    ArrayList<String> err_msg = new ArrayList<>();

    // stores in a format of key, value, key, value ...
    // in pass two, this is specifically used for detecting error
    ArrayList<Object> key_val_lst = new ArrayList<>();

    // a dictionary mapping the usage of symbol to the correspond index
    HashMap<String, List<Integer>> d = new HashMap<String, List<Integer>>();
    for (Map.Entry<String, Integer> pair : dict.entrySet()) {
      String symbol = pair.getKey();
      // map each symbol to an empty integer array list and record their index
      d.put(symbol,new ArrayList<Integer>());
    }
    String cur_symbol="";
    // declare use list flags for complete status
    boolean use_lst_comp = true;
    boolean get_num_of_use_types = false;
    int remaining_use_types = 0;

    // declare base address flags for complete status
    boolean base_comp = true;
    boolean get_module_len = false;
    int module_len = 0;
    int walker = 0;
    int instruction_num = 0;
    ArrayList<Integer> entry_lst = new ArrayList<Integer>();
    // in format of symbol,num of instruction in current module... repeatedly
    ArrayList<Object> symbol_order = new ArrayList<Object>();
    HashMap<Integer,Boolean> modified_map = new HashMap<Integer,Boolean>();
    // maps absolute index of entry lists to base address
    HashMap<Integer,Integer> base_addr_map = new HashMap<Integer,Integer>();
    int pair_in_cur_module = 0;
    boolean multiple_define_error_flag = false;
    // book keeping remaining modules
    int module_number=Integer.MIN_VALUE;

    while (ask_for_input){

      // the user have completed the second pass
      if (module_number==0){
        ask_for_input = false;

        // warning checking: whether a symbol is defined but not used
        for (Map.Entry<String, List<Integer>> pairs : d.entrySet()) {
          String ks = pairs.getKey();
          // warning checking: whether a symbol is defined but not used
          if(d.get(ks).size()==0){
            err_msg.add("Warning: Symbol "+ks+" is defined but not used.");
          }
        }

        // begin analyzing entry table
        // resolving externel reference
        for(int i=0;i<symbol_order.size();i+=2){
          String key = (String)symbol_order.get(i);
          int num_of_instruction = (Integer)symbol_order.get(i+1);

          // invalid key
          if (!d.containsKey(key)){
            key += "invalid";
            for(int j=0;j<num_of_instruction;++j){
              // extract invalid index
              int invalid_ind = d.get(key).get(j);
              int invalid_addr = entry_lst.get(invalid_ind);
              // error check whether the given index has already been modified
              if (modified_map.containsKey(invalid_ind))
                err_msg.add("Error: Multiple symbols are listed as used in the same instruction: "+invalid_addr + "; all but last ignored.");
              // invalid address would be reinterpreted as 111 by protocal
              entry_lst.set(invalid_ind,(invalid_addr/10000*1000)+111);
              modified_map.put(invalid_ind,true);
            }
          }
          // valid key - external reference type
          else if(d.containsKey(key)){
            for(int k=0;k<num_of_instruction;++k){
              int ind_num = d.get(key).get(k);
              int addr = entry_lst.get(ind_num);

              // extract absolute address of symbol to resolve external address type
              int abs_machine_addr = dict.get(key);
              // no machine address should greater than or equal to the size of machine (300)
              if (abs_machine_addr > MAX_PHYSICAL_ADDRESS){
                abs_machine_addr = MAX_PHYSICAL_ADDRESS;
                err_msg.add("Error: Absolute address: "+abs_machine_addr+" exceeds the size of the machine; largest legal value used.");
              }

              if(modified_map.containsKey(ind_num)){
                // resume the entry number to intial state
                addr = addr/10*100+addr%10;
                entry_lst.set(ind_num,addr);
                // raise an error flag for multiple defined error
                multiple_define_error_flag = true;
              }

              // calculate correspond absolute machine address
              entry_lst.set(ind_num,addr/10000*1000+abs_machine_addr);
              // catch an error flag, prepare error information
              if(multiple_define_error_flag){
                err_msg.add("Error: Multiple symbols are listed as used in the same instruction: "+entry_lst.get(ind_num)+ "; all but last ignored.");
              }
              modified_map.put(ind_num,true);
              multiple_define_error_flag = false;
            }
          }

          // remove the number of instrustions in the symbol to abs index map
          for(int qd=0; qd<num_of_instruction; ++qd)
            d.get(key).remove(0);
        }

        // immediate, relative, absolute entries
        for(int p=0;p<entry_lst.size();++p){
          // un-modified entries
          if(!modified_map.containsKey(p)){
            int addr = entry_lst.get(p);
            int machine_addr = addr%10000/10;

            int status = addr%10;
            // immediate or absolute entry case
            if(status==1 || status==2){
              // if this is an absolute entry, check whether absolute address
              // exceeds the MAX_PHYSICAL_ADDRESS of the machine
              if(status==2 && (machine_addr>MAX_PHYSICAL_ADDRESS)){
                  err_msg.add("Error: Absolute address: "+machine_addr+" exceeds the size of the machine; largest legal value used.");
                  // correct the abs address to MAX_PHYSICAL_ADDRESS in machine
                  machine_addr = MAX_PHYSICAL_ADDRESS;
              }
              entry_lst.set(p,addr/10000*1000+machine_addr);
            }
            // relative entry case
            else if(status==3){
              // no machine address should greater than or equal tothe size of machine (300)
              // error detected, modify the address to 299 following protocal
              int cur_base_number = base_addr_map.get(p);
              if(machine_addr + cur_base_number > MAX_PHYSICAL_ADDRESS){
                entry_lst.set(p,addr/10000*1000+MAX_PHYSICAL_ADDRESS);
                err_msg.add("Error: Absolute address "+machine_addr + cur_base_number+" exceeds the size of the machine; largest legal value used.");
              }
              // error not detected, proceed normal operation
              else{
                entry_lst.set(p,addr/10000*1000+machine_addr+cur_base_number);
                modified_map.put(p,true);
              }
            }
          }
          else{
            continue;
          }
        }
      }

      // the user have not yet complete all the inputs
      else{
        String input = in.nextLine();
        List<String> token = purifyInput(input);

        for(int i=0;i<token.size();++i){
          // the first valid input number would always be module number
          if(!read_module_number && isNumber(token.get(i))){
            read_module_number = true;
            module_number = Integer.parseInt(token.get(i));
            continue;
          }
          else if(def_lst_comp && use_lst_comp && base_comp){
            // start analyze definition list
            def_lst_comp = false;
          }
          // begin analyziang definition list
          if (!def_lst_comp){
            if (!get_num_of_defs){
              pair_in_cur_module = Integer.parseInt(token.get(i));
              remaining_def_elem = 2 * pair_in_cur_module;

              get_num_of_defs = true;
              if (remaining_def_elem == 0){
                def_lst_comp = true;
                get_num_of_defs = false;
                // switch to use list analysis
                use_lst_comp = false;
              }
            }
            else if(get_num_of_defs && remaining_def_elem!=0){
              if(isNumber(token.get(i))){
                key_val_lst.add(Integer.parseInt(token.get(i))+base_address);
              }
              --remaining_def_elem;
              if(remaining_def_elem==0){
                def_lst_comp = true;
                get_num_of_defs = false;
                // switch to use list analysis
                use_lst_comp = false;
              }
            }
          }
          // begin analyzing use list
          else if(!use_lst_comp){
            // the number of use type instructions has not been received
            if (!get_num_of_use_types){
              remaining_use_types = Integer.parseInt(token.get(i));
              get_num_of_use_types = true;
              if(remaining_use_types==0){
                get_num_of_use_types = false;
                use_lst_comp = true;
                // switch to base address analysis
                base_comp = false;
              }
            }
            // the number of use type instructions has been receeived
            else{
              // the current input is a symbol
              if(!isNumber(token.get(i)) && remaining_use_types!=0){
                cur_symbol = token.get(i);
                // add the current symbol to symbol order
                symbol_order.add(cur_symbol);
              }
              // current input is not a symbol
              else if(isNumber(token.get(i)) && remaining_use_types!=0){
                // current input is -1, which represents a sentinal
                if(Integer.parseInt(token.get(i)) == -1){
                  --remaining_use_types;

                  // add the number of instructions (entries) of the symbol
                  symbol_order.add(instruction_num);
                  // clear instruction num to zero for next symbol
                  instruction_num = 0;

                  if(remaining_use_types == 0){
                    get_num_of_use_types = false;
                    use_lst_comp = true;
                    // switch to base address analysis
                    base_comp = false;
                  }
                }
                // current input is an valid use number
                else{
                  instruction_num += 1;
                  // absolute index in the entry list
                  int abs_index = Integer.parseInt(token.get(i)) + base_address;
                  // if this is a valid  (properly defined) symol name
                  if (d.containsKey(cur_symbol)){
                    d.get(cur_symbol).add(abs_index);
                  }
                  else{
                    // invalid (undefined) symbol name
                    // if invalid symbol have not mapped with its entry index
                    if(!d.containsKey(cur_symbol+"invalid")){
                      // establish a mapping relationship
                      d.put(cur_symbol + "invalid",new ArrayList<Integer>());
                    }
                    // update the entry index of the invalid symbol
                    d.get(cur_symbol + "invalid").add(abs_index);
                    err_msg.add("Error: The symbol "+cur_symbol+ " is used but not defined; 111 used.");
                  }
                }
              }
            }
          }

          // begin analyzing base addresses
          else if(!base_comp){
            // module length have not received
            if(!get_module_len){
              module_len = Integer.parseInt(token.get(i));
              // Error checking: no definition should exceed the size of cur module
              // check current module backwards from the key_val_lst
              int cursor = key_val_lst.size()-1;
              for(int j=0;j<pair_in_cur_module;++j){
                if (((Integer)key_val_lst.get(cursor))-base_address >= module_len){
                  // error detected: append the abs index to the remove lst
                  remove_lst.add((Integer)key_val_lst.get(cursor));
                }
                else{
                  cursor-=2*j;
                }
              }
              get_module_len = true;
              // update base address based on the current module length
              walker = module_len;
              if(walker == 0){
                get_module_len = false;
                base_comp = true;
                --module_number;
                base_address += module_len;
              }
            }
            // module length have been received
            else{
              // add all entries to an entry list to be processed later
              entry_lst.add(Integer.parseInt(token.get(i)));

              // map the absolute index in entry lst to currrent base address
              base_addr_map.put(entry_lst.size()-1,base_address);

              // walker records the num of remaining entries
              --walker;
              if (walker == 0){
                get_module_len = false;
                base_comp = true;
                --module_number;
                // update base address
                base_address += module_len;
              }
            }
          }
        }
      }
    }
    in.close();
    dispErrMsg(err_msg);

    return entry_lst;
  }
}
