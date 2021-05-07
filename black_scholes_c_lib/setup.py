from distutils.core import setup, Extension

module1 = Extension('OptionsPricing', sources = ['options_pricing.c'])

setup (name = 'OptionsPricing',
        version = '1.0',
        description = 'Calculates the volitility and Greeks of options using different methods',
        ext_modules = [module1])
