import os
from flask import *
from werkzeug.utils import secure_filename
import glob
# from flaskext.markdown import Markdown
from flask_misaka import Misaka
import numpy as np
import pandas as pd
import subprocess
import shutil
import json
# from flask import jsonify

# import docker

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

from brainPainterRepo import fileFormatChecker

UPLOAD_FOLDER = '/research/brain-coloring-website/uploads'
REPO_DIR = os.getcwd()
ALLOWED_EXTENSIONS = {'csv'}

TOKEN = open(os.path.expanduser('~/.flaskToken'), 'r').read()[:-1]

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = TOKEN
# Markdown(app,safe_mode=False,
#               output_format='html5')
Misaka(app, fenced_code=True, tables=True, quote=True, autolink=True, math=True, math_explicit=True, highlight=True)


from brainPainterRepo import config

BRAIN_TYPE = config.BRAIN_TYPE
IMG_TYPE = config.IMG_TYPE
COLORS_RGB = config.COLORS_RGB
RESOLUTION = config.RESOLUTION
BACKGROUND_COLOR = config.BACKGROUND_COLOR
IMG_SETTINGS = []

DOCKER=True

# import socket
# if socket.gethostname() == 'sesame':
#   DOCKER=False

procDetails = {}
procDetails['testHash']= {}
procDetails['testHash']['nrRowsDf'] = 1



def generateConfigText(INPUT_FILE, OUTPUT_FOLDER, ATLAS, BRAIN_TYPE, IMG_TYPE, COLORS_RGB, RESOLUTION, BACKGROUND_COLOR):
  text = "ATLAS='%s'" % ATLAS + '\n\n'
  text += "INPUT_FILE='%s'" % INPUT_FILE + '\n\n'
  text += "OUTPUT_FOLDER = '%s'" % OUTPUT_FOLDER + '\n\n'
  text += "BRAIN_TYPE = '%s'" % BRAIN_TYPE + '\n\n'
  text += "IMG_TYPE = '%s'" % IMG_TYPE + '\n\n'
  text += "COLORS_RGB = %s" % str(COLORS_RGB) + '\n\n'
  text += "RESOLUTION = %s" % str(RESOLUTION) + '\n\n'
  text += "BACKGROUND_COLOR = %s" % str(BACKGROUND_COLOR) + '\n\n'
  text += "cortAreasIndexMapDK = %s" % str(config.cortAreasIndexMapDK) + '\n\n'
  text += "cortAreasIndexMapMice = %s" % str(config.cortAreasIndexMapMice) + '\n\n'
  text += "cortAreasIndexMapDestrieux = %s" % str(config.cortAreasIndexMapDestrieux) + '\n\n'
  text += "cortAreasIndexMapTourville = %s" % str(config.cortAreasIndexMapTourville) + '\n\n'
  text += "subcortMouseAreasIndexMap = %s" % str(config.subcortMouseAreasIndexMap) + '\n\n'
  text += "subcortAreasIndexMap = %s" % str(config.subcortAreasIndexMap) + '\n\n'
  text += "requestFromWebsite = True" + '\n\n'


  return text

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def processFile(hash, fullFilePath, ATLAS, BRAIN_TYPE, IMG_TYPE, COLORS_RGB, RESOLUTION,
                            BACKGROUND_COLOR, CONFIG_FILE, LOG_FILE):

  #OUTPUT_FOLDER = '../static/generated/%s' % hash
  OUTPUT_FOLDER = 'generated/%s' % hash

  text = generateConfigText(fullFilePath, OUTPUT_FOLDER, ATLAS, BRAIN_TYPE, IMG_TYPE, COLORS_RGB, RESOLUTION,
                            BACKGROUND_COLOR)

  print('writing to CONFIG FILE: %s' % CONFIG_FILE)
  with open(CONFIG_FILE, 'w') as f:
    f.write(text)


  # check input file for errors
  matDf = pd.read_csv(fullFilePath)

  global procDetails
  procDetails[hash]['nrRowsDf'] = matDf.shape[0]

  if ATLAS == 'DK':
    cortAreasIndexMap = config.cortAreasIndexMapDK
    subcortAreasIndexMap = config.subcortAreasIndexMap
  elif ATLAS == 'Destrieux':
    cortAreasIndexMap = config.cortAreasIndexMapDestrieux
    subcortAreasIndexMap = config.subcortAreasIndexMap
  elif ATLAS == 'Tourville':
    cortAreasIndexMap = config.cortAreasIndexMapTourville
    subcortAreasIndexMap = config.subcortAreasIndexMap
    ATLAS = 'DKT'  # actually 3D models are labelled as DKT
  elif ATLAS == 'Mice':
      cortAreasIndexMap = config.cortAreasIndexMapMice
      subcortAreasIndexMap = config.subcortMouseAreasIndexMap
  elif ATLAS == 'Custom':
    cortAreasIndexMap = config.cortAreasIndexMapCustom
    subcortAreasIndexMap = config.subcortAreasIndexMapCustom
  else:
    raise ValueError('ATLAS has to be either \'DK\', \'Destrieux\', \'Tourville\', \'Mice\' or \'Custom\' ')

  cortRegionsThatShouldBeInTemplate = list(cortAreasIndexMap.values())
  subcortRegionsThatShouldBeInTemplate = list(subcortAreasIndexMap.values())
  regionsThatShouldBeInTemplate = cortRegionsThatShouldBeInTemplate + subcortRegionsThatShouldBeInTemplate

  errorMsg = fileFormatChecker.checkInputDf(matDf, regionsThatShouldBeInTemplate, getErrorAsStr = True)

  if errorMsg != '':
    # flash(errorMsg)
    return errorMsg




  if DOCKER:
    HOST_DIR = '%s/static/generated/' % REPO_DIR
    DOCKER_DIR = '/home/brain-coloring/generated/'
    IMG_NAME = 'mrazvan22/brain-coloring-v2'
    INNER_CMD = 'cd /home/brain-coloring; configFile=%s blender --background --python blendCreateSnapshot.py > %s/%s_log.txt' % (CONFIG_FILE, OUTPUT_FOLDER, IMG_TYPE)

    cmd = 'docker run  --mount src=%s,target=%s,type=bind' \
          ' %s /bin/bash -c \'%s\' ' % (HOST_DIR, DOCKER_DIR, IMG_NAME, INNER_CMD)

    print(cmd)
    subprocess.Popen(('chmod -R 777 %s/%s' % (HOST_DIR, hash)), shell=True).wait()
    # os.system('chmod -R 777 %s/%s' % (HOST_DIR, hash))

    # os.system(cmd)

    proc = subprocess.Popen(
      cmd,  # call something with a lot of output so we can see it
      shell=True,
      stdout=subprocess.PIPE,
      universal_newlines=True
    )

    # DOCKER_CMD = 'configFile=%s blender --background --python blendCreateSnapshot.py' % CONFIG_FILE
    #
    # client = docker.from_env()
    # volumes = {HOST_DIR: {'bind': DOCKER_DIR, 'mode': 'rw'}}
    # container = client.containers.run(IMG_NAME, command='/bin/bash; echo "--------XXXXXXXX-------"; ls; pwd', working_dir='/home/brain-coloring',
    #                                   volumes=volumes, detach=True)
    # print('logs', container.logs())

    # asd

    procDetails[hash]['procList'] += [proc]
    # procDetails[hash]['procList'] += [container]

  else:
    cmd ='cd brainPainterRepo;  configFile=../%s blender --background --python blendCreateSnapshot.py' % CONFIG_FILE

    print(cmd)
    os.system('pwd')
    # os.system(cmd)
    subprocess.Popen(cmd, shell=True).wait()


  return ''


def renderDefTemplate(hash=json.dumps('testHash'), galleryDisabled='disabled'):
  #figPaths = [0, 0, 0, 0, 0, 0]
  srcFld = 'static/example2'

  #figPaths[0] = '%s/Image_1_cortical-outer.png' % srcFld
  #figPaths[1] = '%s/Image_1_cortical-inner.png' % srcFld
  #figPaths[2] = '%s/Image_1_subcortical.png' % srcFld
  #figPaths[3] = '%s/Image_2_cortical-outer.png' % srcFld
  #figPaths[4] = '%s/Image_2_cortical-inner.png' % srcFld
  #figPaths[5] = '%s/Image_2_subcortical.png' % srcFld


  #print('pwd', os.system('pwd'))
  figPaths = glob.glob("%s/*.png" % srcFld)
  print('figPaths Def', figPaths)
  figPaths = list(np.sort(figPaths))
  #figPaths = ['../../static/generated/%s/%s' % (hash, x.split('/')[-1]) for x in figPaths]

  figDescs = [x.split('/')[-1][:-4] for x in figPaths]
  figDescsShort = ['_'.join(x.split('_')[1:]) for x in figDescs]
  figDescsShort = [x[:17] for x in figDescsShort]
  print('figPaths Def', figPaths)
  print('figDescs Def', figDescs)


  #figDescs = [x.split('/')[-1][:-4] for x in figPaths]
  #figDescsShort = [x[:17] for x in figDescs]
  zipLocation = '%s/figures.zip' % srcFld

  return render_template('index.html', figPaths = figPaths, figDescs = figDescs, galleryDisabled=galleryDisabled,
                         zipLocation=zipLocation, figDescsShort=figDescsShort, hash=hash, errorImageGen=0)



@app.route('/', methods=['GET', 'POST'])
def index():
  # genDir = glob.glob("generated/*/")
  # if len(genDir) >= 9: 
  #   # deletes generated subdirs after use
  #   for subDir in genDir:
  #     shutil.rmtree(subDir)
  # print("Tau")

  if request.method == 'POST':
    # check if the post request has the file part
    if 'file' not in request.files:
      flash('No file part')
      return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
      flash('No selected file')
      return redirect(request.url)
    if file and allowed_file(file.filename):
      import random
    if IMG_SETTINGS == []:
      flash('No modes/angles selected')
      return redirect(request.url)

  return renderDefTemplate()




@app.route('/generated', methods=['GET', 'POST'])
def generated():
  if request.method == 'POST':
    # check if the post request has the file part
    if 'file' not in request.files:
      flash('No file part')
      return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
      flash('No selected file')
      return redirect(request.url)
    if file and allowed_file(file.filename):
      import random
      hash = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
      filename = hash + '_' + secure_filename(file.filename)


      print(request.form)
      print(request.form['c5'])

      BRAIN_TYPE = request.form['brainType']
      ANGLES = request.form.getlist('angles')
      MODES = request.form.getlist('modes')
      COLORS_RGB = parseCol(request.form['c1']) + parseCol(request.form['c2']) + parseCol(request.form['c3']) + \
                   parseCol(request.form['c4']) + parseCol(request.form['c5'])
      BACKGROUND_COLOR = parseCol(request.form['backgroundCol'])[0]
      RESOLUTION = parseCommaSepStr(request.form['resolution'], int)[0]

      # asda


      ATLAS = request.form['atlas']
      if ATLAS == 'Desikan-Killiany':
        ATLAS = 'DK'

      # convert user input into image settings

      if 'cortical-outer' in MODES:
        if 'right-hemisphere' in ANGLES: IMG_SETTINGS.append('cortical-outer-right-hemisphere')
        if 'left-hemisphere' in ANGLES: IMG_SETTINGS.append('cortical-outer-left-hemisphere')
      if 'cortical-inner' in MODES:
        if 'right-hemisphere' in ANGLES: IMG_SETTINGS.append('cortical-inner-right-hemisphere')
        if 'left-hemisphere' in ANGLES: IMG_SETTINGS.append('cortical-inner-left-hemisphere')
      if 'subcortical' in MODES: IMG_SETTINGS.append('subcortical')
      if 'top' in ANGLES: IMG_SETTINGS.append('top')
      if 'bottom' in ANGLES: IMG_SETTINGS.append('bottom')

      if len(IMG_SETTINGS) == 0:
        flash('No angles/modes selected')
        return redirect(request.url)

      print('IMAGE SETTINGS', IMG_SETTINGS)
      print('BRAIN_TYPE', BRAIN_TYPE)
      print('COLORS_RGB', COLORS_RGB)
      print('BACKGROUND_COLOR', BACKGROUND_COLOR)
      print('RESOLUTION', RESOLUTION)

      print('lalalalaaa 2')



      EXP_DIR = '%s/static/generated/%s' % (REPO_DIR, hash)
      fullFilePath = os.path.join(EXP_DIR, filename)
      print('fullFilePath', fullFilePath)
      subprocess.Popen(('mkdir -p %s' % EXP_DIR), shell=True).wait()
      # os.system('mkdir -p %s' % EXP_DIR)
      file.save(fullFilePath)
      LOG_FILE = '%s/log-blender.txt' % EXP_DIR

      partialFilePath = 'generated/%s/%s' % (hash, filename)
      errorMsgs = []

      global procDetails
      procDetails[hash] = {}
      procDetails[hash]['procList'] = []

      for IMG_TYPE in IMG_SETTINGS:
        CONFIG_FILE = 'generated/%s/%s_config.py' % (hash, IMG_TYPE)
        errorMsgs += [processFile(hash, partialFilePath, ATLAS, BRAIN_TYPE, IMG_TYPE, COLORS_RGB, RESOLUTION,
                              BACKGROUND_COLOR, CONFIG_FILE, LOG_FILE)]

      print('errorMsgs', errorMsgs)
      errorMsgsUnq = np.unique([e for e in errorMsgs if e != ''])

      for e in errorMsgsUnq:
        for subErs in e.split('\n\n'):
          #flash(e.replace('\n\n', '<br/>'))
          flash(subErs)

      if len(errorMsgsUnq) > 0:
        return renderDefTemplate()


      return render_template('processing.html',hash=json.dumps(hash))



  # return render_template('processing.html', hash=json.dumps('testHash'))
  return renderDefTemplate()




@app.route('/generated/<hash>')
def generateForHash(hash):
    EXP_DIR = 'static/generated/%s' % hash

    print('running pdflatex')
    pdflatexCmd = 'cd static/generated/%s; pdflatex report.tex' % hash
    #os.system(pdflatexCmd)
    #subprocess.Popen(
    #  pdflatexCmd,  # call something with a lot of output so we can see it
    #  shell=True,
    #  stdout=subprocess.PIPE,
    #  universal_newlines=True
    #)

    zipCmd = 'cd static/generated/%s; pdflatex -interaction=nonstopmode report.tex; zip -r figures.zip *.png *.txt *.tex *.pdf' % hash
    # subprocess.Popen(
    #   zipCmd,  # call something with a lot of output so we can see it
    #   shell=True,
    #   stdout=subprocess.PIPE,
    #   universal_newlines=True
    # )
    os.system(zipCmd)

    # if errorImgGen = 1, then some images could not be generated
    errorImgGen = request.args.get('error', None)


    figPaths = glob.glob("%s/*.png" % EXP_DIR)
    figPaths = list(np.sort(figPaths))

    figPaths = ['../../static/generated/%s/%s' % (hash, x.split('/')[-1]) for x in figPaths]

    figDescs = [x.split('/')[-1][:-4] for x in figPaths]
    figDescsShort = ['_'.join(x.split('_')[1:]) for x in figDescs]
    figDescsShort = [x[:17] for x in figDescsShort]
    print('figPaths', figPaths)
    print('figDescs', figDescs)
    # asda
    zipLocation = os.path.join('../../static/generated/%s' % hash, 'figures.zip')


    # return render_template('processing.html', hash=json.dumps(hash))

    return render_template('index.html', figPaths=figPaths, figDescs=figDescs, galleryDisabled='',
                           zipLocation=zipLocation, figDescsShort=figDescsShort, hash=json.dumps(hash), errorImgGen=errorImgGen)


@app.route('/progress/<hash>')
def progress(hash):
    EXP_DIR = 'static/generated/%s' % hash
    imagesSoFar = glob.glob('%s/*.png' % EXP_DIR)
    nrImagesSoFar = len(imagesSoFar)

    print('pwd')
    os.system('pwd')
    global procDetails
    print('imagesSoFar', imagesSoFar)
    print('procDetails', procDetails)
    nrRowsDf = procDetails[hash]['nrRowsDf']
    progress = int(100 * float(nrImagesSoFar) / (nrRowsDf * len(IMG_SETTINGS)))

    # A None value indicates that the process hasn't terminated yet.
    procFinished = [p.poll() is not None for p in procDetails[hash]['procList']]
    print('procFinished', procFinished)

    error = 0
    if np.all(procFinished) and progress < 100:
      # some images were not generated, throw error
      error = 1

    print('progress', progress)

    return jsonify(newProgress=progress, error=error)

def parseCommaSepStr(strCol, convFunc=float):
  if strCol != '':
    return [tuple([convFunc(i) for i in strCol.split(',') ])]
  else:
    return []

def parseCol(strCol):
  print(strCol)
  rgbCol = tuple(int(strCol[i:i+2], 16) for i in (0, 2, 4))
  rgbCol = (float(rgbCol[0])/255, float(rgbCol[1])/255, float(rgbCol[2])/255)
  print(rgbCol)
  return [rgbCol]




from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
  return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# from gevent.pywsgi import WSGIServer
# from yourapplication import app
# from gevent import wsgi
#
# server = wsgi.WSGIServer(('127.0.0.1', 5000), app)
# server.serve_forever()

if __name__ == '__main__':

    # app.secret_key = 'super secret key'
    # app.config['SESSION_TYPE'] = 'filesystem'
    #
    # sess.init_app(app)

    app.debug = True
    app.run(host = '0.0.0.0', port=int("80"), processes=15, debug=True)
