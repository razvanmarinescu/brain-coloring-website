
import os
from flask import *
from werkzeug.utils import secure_filename
import glob
# from flaskext.markdown import Markdown
from flask_misaka import Misaka
import numpy as np

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
COLORS_RGB =config.COLORS_RGB
RESOLUTION = config.RESOLUTION
BACKGROUND_COLOR = config.BACKGROUND_COLOR


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
  text += "cortAreasIndexMapDestrieux = %s" % str(config.cortAreasIndexMapDestrieux) + '\n\n'
  text += "cortAreasIndexMapTourville = %s" % str(config.cortAreasIndexMapTourville) + '\n\n'
  text += "subcortAreasIndexMap = %s" % str(config.subcortAreasIndexMap) + '\n\n'

  return text

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def processFile(hash, fullFilePath, ATLAS, BRAIN_TYPE, IMG_TYPE, COLORS_RGB, RESOLUTION,
                            BACKGROUND_COLOR, CONFIG_FILE):

  OUTPUT_FOLDER = '../generated/%s' % hash

  text = generateConfigText(fullFilePath, OUTPUT_FOLDER, ATLAS, BRAIN_TYPE, IMG_TYPE, COLORS_RGB, RESOLUTION,
                            BACKGROUND_COLOR)


  with open(CONFIG_FILE, 'w') as f:
    f.write(text)

  cmd ='cd brainPainterRepo;  configFile=../%s blender --background --python blendCreateSnapshot.py' % CONFIG_FILE
  print(cmd)
  os.system('pwd')
  os.system(cmd)



  return 'File uploaded successfully'




@app.route('/', methods=['GET', 'POST'])
def index():
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

      fullFilePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

      # file.save(fullFilePath)
      # processFile(hash, fullFilePath)

  # form = ReusableForm()

  figPaths = [0, 0, 0, 0, 0, 0]
  srcFld = '../static/example'

  figPaths[0] = '%s/Image_1_cortical-outer.png' % srcFld
  figPaths[1] = '%s/Image_1_cortical-inner.png' % srcFld
  figPaths[2] = '%s/Image_1_subcortical.png' % srcFld
  figPaths[3] = '%s/Image_2_cortical-outer.png' % srcFld
  figPaths[4] = '%s/Image_2_cortical-inner.png' % srcFld
  figPaths[5] = '%s/Image_2_subcortical.png' % srcFld


  figDescs = [x.split('/')[-1][:-4] for x in figPaths]
  figDescsShort = [x[:17] for x in figDescs]
  zipLocation = '%s/figures.zip' % srcFld

  return render_template('index.html', figPaths = figPaths, figDescs = figDescs, galleryDisabled='disabled', zipLocation=zipLocation, figDescsShort=figDescsShort)



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
      COLORS_RGB = parseCol(request.form['c1']) + parseCol(request.form['c2']) + parseCol(request.form['c3']) + \
                   parseCol(request.form['c4']) + parseCol(request.form['c5'])
      BACKGROUND_COLOR = parseCol(request.form['backgroundCol'])[0]
      RESOLUTION = parseCommaSepStr(request.form['resolution'], int)[0]
      # asda


      ATLAS = request.form['atlas']
      if ATLAS == 'Desikan-Killiany':
        ATLAS = 'DK'



      print('BRAIN_TYPE', BRAIN_TYPE)
      print('COLORS_RGB', COLORS_RGB)
      print('BACKGROUND_COLOR', BACKGROUND_COLOR)
      print('RESOLUTION', RESOLUTION)

      print('lalalalaaa 2')


      EXP_DIR = '%s/static/generated/%s' % (REPO_DIR, hash)
      fullFilePath = os.path.join(EXP_DIR, filename)
      print('fullFilePath', fullFilePath)
      os.system('mkdir -p %s' % EXP_DIR)
      file.save(fullFilePath)

      for IMG_TYPE in ['cortical-outer', 'cortical-inner', 'subcortical']:
        CONFIG_FILE = 'generated/%s/%s_config.py' % (hash, IMG_TYPE)
        processFile(hash, fullFilePath, ATLAS, BRAIN_TYPE, IMG_TYPE, COLORS_RGB, RESOLUTION,
                              BACKGROUND_COLOR, CONFIG_FILE)

      zipCmd = 'cd generated/%s; zip -r figures.zip *.png' % hash
      os.system(zipCmd)

      OUTPUT_FOLDER = 'generated/%s' % (hash)

      # figPaths = [0, 0, 0]
      # figPaths[0] = os.path.join('../static/generated', '%s/cortical-back_0.png')
      # figPaths[1] = os.path.join('../static/generated', '39F1DD8350DAE7FB/cortical-back_1.png')
      # figPaths[2] = os.path.join('../static/generated', '39F1DD8350DAE7FB/cortical-back_1.png')

      figPaths = glob.glob("%s/*.png" % EXP_DIR)
      figPaths = list(np.sort(figPaths))

      figPaths = ['../static/generated/%s/%s' % (hash, x.split('/')[-1]) for x in figPaths]

      figDescs = [x.split('/')[-1][:-4] for x in figPaths]
      figDescsShort = [x[:17] for x in figDescs]
      print('figPaths', figPaths)
      print('figDescs', figDescs)
      # asda
      zipLocation = os.path.join('../static/generated/%s' % hash, 'figures.zip')

      return render_template('index.html', figPaths=figPaths, figDescs=figDescs, galleryDisabled='', zipLocation=zipLocation, figDescsShort=figDescsShort)

  return render_template('index.html')

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


def createGalleryHtml(zipLocation):

  return '''

<!doctype html>
<title>Gallery</title>
<head>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">

</head>

<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {
  font-family: Verdana, sans-serif;
  margin: 0;
}

* {
  box-sizing: border-box;
}

.row > .column {
  padding: 0 8px;
}

.row:after {
  content: "";
  display: table;
  clear: both;
}

.rowModal {
  padding: 0 0px;
  margin-bottom: 0px;
}

.column {
  float: left;
  width: 15%;
}

/* The Modal (background) */
.modal {
  display: none;
  position: fixed;
  z-index: 1;
  padding-top: 100px;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: black;
}

/* Modal Content */
.modal-content {
  position: relative;
  background-color: white;
  margin: auto;
  padding: 0;
  width: 90%;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}

/* The Close Button */
.close {
  color: white;
  position: absolute;
  top: 10px;
  right: 25px;
  font-size: 35px;
  font-weight: bold;
}

.close:hover,
.close:focus {
  color: #999;
  text-decoration: none;
  cursor: pointer;
}

.mySlides {
  display: none;
}

.cursor {
  cursor: pointer;
}

/* Next & previous buttons */
.prev,
.next {
  cursor: pointer;
  position: absolute;
  top: 50%;
  width: auto;
  padding: 16px;
  margin-top: -50px;
  color: white;
  font-weight: bold;
  font-size: 20px;
  transition: 0.6s ease;
  border-radius: 0 3px 3px 0;
  user-select: none;
  -webkit-user-select: none;
}

/* Position the "next button" to the right */
.next {
  right: 0;
  border-radius: 3px 0 0 3px;
}

/* On hover, add a black background color with a little bit see-through */
.prev:hover,
.next:hover {
  background-color: rgba(0, 0, 0, 0.8);
}

/* Number text (1/3 etc) */
.numbertext {
  color: #f2f2f2;
  font-size: 12px;
  padding: 8px 12px;
  position: absolute;
  top: 0;
}

img {
  margin-bottom: -4px;
}

.caption-container {
  text-align: center;
  background-color: black;
  padding: 2px 16px;
  color: white;
}

.demo {
  opacity: 0.6;
  margin-bottom: 0px;
}

.active,
.demo:hover {
  opacity: 1;
  margin-bottom: 0px;
}

img.hover-shadow {
  transition: 0.3s;
}

.hover-shadow:hover {
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
}
</style>


<body class="body">


<!-- Images used to open the lightbox -->
<div class="row">
  <div class="column">
    <img src="''' + figPaths + '''"  style="width:100%" onclick="openModal();currentSlide(1)" class="hover-shadow">
  </div>
  <div class="column">
    <img src="''' + figPaths + '''"  style="width:100%" onclick="openModal();currentSlide(2)" class="hover-shadow">
  </div>
</div>

<!-- The Modal/Lightbox -->
<div id="myModal" class="modal">
  <span class="close cursor" onclick="closeModal()">&times;</span>
  <div class="modal-content">

    <div class="mySlides">
      <div class="numbertext">1 / 2</div>
      <img src="''' + figPaths + '''" style="width:100%">
    </div>

    <div class="mySlides">
      <div class="numbertext">2 / 2</div>
      <img src="''' + figPaths + '''" style="width:100%">
    </div>

    <!-- Next/previous controls -->
    <a class="prev" onclick="plusSlides(-1)">&#10094;</a>
    <a class="next" onclick="plusSlides(1)">&#10095;</a>

    <!-- Caption text -->
    <div class="caption-container">
      <p id="caption"></p>
    </div>

    <!-- Thumbnail image controls -->
    <div class="rowModal">
      <div class="column">
        <img class="demo" src="''' + figPaths + '''" style="width:100%" onclick="currentSlide(1)" alt="Nature">
      </div><div class="column">
        <img class="demo" src="''' + figPaths + '''" style="width:100%" onclick="currentSlide(2)" alt="Snow">
      </div>
    </div>
  </div>
</div>


   <div class="container" align="left">
		<a href="''' + zipLocation + '''" target="blank"><button class='btn btn-default'>Download!</button></a>
   </div>
   
   
<script>
function openModal() {
  document.getElementById("myModal").style.display = "block";
}

function closeModal() {
  document.getElementById("myModal").style.display = "none";
}

var slideIndex = 1;
showSlides(slideIndex);

function plusSlides(n) {
  showSlides(slideIndex += n);
}

function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  var i;
  var slides = document.getElementsByClassName("mySlides");
  var dots = document.getElementsByClassName("demo");
  var captionText = document.getElementById("caption");
  if (n > slides.length) {slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";
  }
  for (i = 0; i < dots.length; i++) {
      dots[i].className = dots[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "block";
  dots[slideIndex-1].className += " active";
  captionText.innerHTML = dots[slideIndex-1].alt;
}
</script>


   
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>




</body>

'''





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
    app.run(host = '0.0.0.0', port=int("80"), debug=True)