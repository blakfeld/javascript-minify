#!/usr/bin/python
'''
Take either a file, or a directory containing
  javascript files, then send them to the
  closure javascript compiler. After compiling
  write the out the mini javascript. This is
  merely a modified verison of the script
  provided by Google.
'''

import httplib, urllib, sys, os
from optparse import OptionParser

def compileJavascript(jsFile, compileType):
  '''
  Take in a javascript file, open it up, and send it to closure.
  Return the compiled javascript
  '''

  try:
    f = open(jsFile, 'r')
    js = f.read()
    f.close()
  except IOError:
    print "Unable to open {0}".format(jsFile)

  params = urllib.urlencode([
      ('js_code', js),
      ('compilation_level', compileType),
      ('output_format', 'text'),
      ('output_info', 'compiled_code'),
    ])

  # Always use the following value for the Content-type header.
  headers = { "Content-type": "application/x-www-form-urlencoded" }
  conn = httplib.HTTPConnection('closure-compiler.appspot.com')
  conn.request('POST', '/compile', params, headers)
  response = conn.getresponse()
  data = response.read()
  conn.close()
  return data

def _main():
  '''
  Main
  '''

  # Set up some Opt flags
  parser = OptionParser()
  parser.add_option("-f", "--file", help="The javascript file to be compiled, or the directory containing the javascript files to be compiled.", action="store", type="string", dest="fileName")
  parser.add_option("-w", "--whitespace-only", help="Specify compile type as WHITESPACE_ONLY (Default)", action="store_const", const="WHITESPACE_ONLY", dest="compileType")
  parser.add_option("-s", "--simple-optimizations", help="Specify compile type as SIMPLE_OPTIMIZATIONS", action="store_const", const="SIMPLE_OPTIMIZATIONS", dest="compileType")
  parser.add_option("-a", "--advanced-optimizations", help="Specify compile type as ADVANCED_OPTIMIZATIONS", action="store_const", const="ADVANCED_OPTIMIZATIONS", dest="compileType")
  parser.add_option("-p", "--print", help="Print output to STDOUT as opposed to a file.", action="store_true", dest="printOut")
  parser.add_option("-q", "--quiet", help="Supress non error messages. This means files will be overwritten without asking.", action="store_true", dest="quiet")
  (opts, args) = parser.parse_args()

  if opts.compileType is None:
    compileType = 'WHITESPACE_ONLY'
  else:
    compileType = opts.compileType

  # Check if we're given a file or directory
  if os.path.isfile(opts.fileName):
    jsFile = opts.fileName
    if '.min.js' in jsFile:
      print "This seems to already be minified?"
      sys.exit(0)

    minFile = os.path.splitext(jsFile)[0] + '.min.js'

    # Don't bother to compile the javascript if we arent' overwriting an existing file.
    if os.path.exists(minFile) and not opts.quiet and not opts.printOut:
      while True:
        overwrite = raw_input("\nWARNING: {0} exits! Overwrite? [y|n] ".format(minFile))
        if overwrite == "yes" or overwrite == "y":
          print "Overwriting.\n"
          break
        elif overwrite == "no" or overwrite == "n":
          print "Exiting."
          sys.exit(0)
        else:
          print "Please enter yes or no."
    
    if not opts.quiet:
        print "Compiling {0}...".format(jsFile)
    minJs = compileJavascript(jsFile, compileType)

    if opts.printOut:
      print minJs
    else:
      try:
        f = open(os.path.splitext(jsFile)[0] + '.min.js', 'w')
        f.write(minJs)
        f.close()
      except IOError:
        print "Unable to write min file for {0}".format(jsFile)
  
  elif os.path.isdir(opts.fileName):
    jsPath = opts.fileName
    jsFiles = os.listdir(jsPath)

    for script in jsFiles:
      # Don't re-min a min.
      if '.min.js' in script:
        continue

      minFile = jsPath + '/' + os.path.splitext(script)[0] + '.min.js'

      # Don't bother to compile the javascript if we arent' overwriting an existing file.
      if os.path.exists(minFile) and not opts.quiet and not opts.printOut:
        continueOuterLoop = False
        while True:
          overwrite = raw_input("\nWARNING: {0} exits! Overwrite? [y|n] ".format(minFile))
          if overwrite == "yes" or overwrite == "y":
            print "Overwriting.\n"
            break
          elif overwrite == "no" or overwrite == "n":
            print "Continuing to next"
            continueOuterLoop = True
            break
          else:
            print "Please enter yes or no."
      
      if continueOuterLoop:
        continueOuterLoop = False
        continue

      if not opts.quiet:
        print "Compiling {0}...".format(script)
      minJs = compileJavascript(jsPath + '/' + script, compileType)

      if opts.printOut:
        print minJs
      else:
        try:
          f = open(jsPath + '/' + os.path.splitext(script)[0] + '.min.js', 'w')
          f.write(minJs)
          f.close()
        except IOError:
          print "Unable to write min file for {0}".format(jsFile)
  else:
    print "A file must be supplied."

  if not opts.quiet:
    print "\nDone!\n"
  sys.exit(0)

if __name__ == "__main__":
  _main()
