import AmpScan.core as core
import AmpScan.trim as trim

if __name__ == '__main__':
    import doctest
    doctest.testmod(core, verbose=True)
    doctest.testmod(trim, verbose=True)

