import test_parser_base
import test_parser_atr

if __name__ == '__main__':
    try:
        test_parser_atr.main()
    except Exception, msg:
        import traceback
        test_parser_base.print_log("error msg:%s" % (msg))
        test_parser_base.print_log("error position:%s" % (traceback.print_exc()))
        a=raw_input()