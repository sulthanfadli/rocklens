import os
import uuid
import flask
import urllib
from PIL import Image
from tensorflow.keras.models import load_model
from flask import Flask, render_template, request, send_file
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = load_model(os.path.join(BASE_DIR, 'model.hdf5'))

ALLOWED_EXT = set(['jpg', 'jpeg', 'png', 'jfif'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT


classes = ['Breccia (Breksi)', 'Claystone (Batulempung)', 'Conglomerate (Konglomerat)', 'Sandstone (batupasir)', 'Siltstone (Batulanau)']


def predict(filename, model):
    img = load_img(filename, target_size=(150, 150))
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)

    img = np.vstack([img])
    result = model.predict(img)

    dict_result = {}
    for i in range(5):
        dict_result[result[0][i]] = classes[i]

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:3]

    prob_result = []
    class_result = []
    for i in range(3):
        prob_result.append((prob[i] * 100).round(2))
        class_result.append(dict_result[prob[i]])

    return class_result, prob_result


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/tools')
def tools():
    return render_template("tools.html")

@app.route('/plans')
def plans():
    return render_template("plans.html")

@app.route('/events')
def events():
    return render_template("events.html")

@app.route('/success', methods=['GET', 'POST'])
def success():
    error = ''
    target_img = os.path.join(os.getcwd(), 'static/images')
    if request.method == 'POST':
        if (request.form):
            link = request.form.get('link')
            try:
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename + ".jpg"
                img_path = os.path.join(target_img, filename)
                output = open(img_path, "wb")
                output.write(resource.read())
                output.close()
                img = filename

                class_result, prob_result = predict(img_path, model)

                predictions = {
                    "class1": class_result[0],
                    "class2": class_result[1],
                    "class3": class_result[2],
                    "prob1": prob_result[0],
                    "prob2": prob_result[1],
                    "prob3": prob_result[2],
                }

                if predictions == "Breccia (Breksi)":
                    desctription = "Breccia"
                elif predictions == "Claystone (Batulempung)":
                    desctription =  "Claystone"
                elif predictions == "Conglomerate (Konglomerat)":
                    desctription = "Conglomerate"
                elif predictions == "Sandstone (batupasir)":
                    desctription = "Sandstone"
                else:
                    desctription = "Siltstone"

            except Exception as e:
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'

            if (len(error) == 0):
                return render_template('success.html', img=img, predictions=predictions, desctription=desctription)
            else:
                return render_template('tools.html', error=error)


        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img, file.filename))
                img_path = os.path.join(target_img, file.filename)
                img = file.filename

                class_result, prob_result = predict(img_path, model)

                predictions = {
                    "class1": class_result[0],
                    "class2": class_result[1],
                    "class3": class_result[2],
                    "prob1": prob_result[0],
                    "prob2": prob_result[1],
                    "prob3": prob_result[2],
                }

                if predictions['class1']  == "Breccia (Breksi)":
                    warna =" hijau kekuningan atau coklat keputih-putihan."
                    ukuran = ">2milimeter "
                    kemas = "Terbuka"
                    sortasi = "Buruk "
                    bentuk = "Angular (menyudut) "
                    porosity = "10-30% "
                    permeability = "Moderate"
                elif predictions['class1']  == "Claystone (Batulempung)":
                    warna = "warna : warna segar kuning kecoklatan, warna lapuk coklat kehitaman."
                    ukuran = "ukuran butir : >2milimeter "
                    kemas = "kemas : Terbuka"
                    sortasi = "sortasi : Buruk"
                    bentuk = "bentuk butir : Rounded (membundar)"
                    porosity = "porosity : 10-30%"
                    permeability = "permeability : Moderate "
                elif predictions['class1']  == "Conglomerate (Konglomerat)":
                    warna = "warna : coklat muda, coklat, kuning, merah, abu-abu dan putih."
                    ukuran = "ukuran butir : 1/16-2 milimeter"
                    kemas = "kemas : Tertutup"
                    sortasi = "sortasi : Sedang"
                    bentuk = "bentuk butir : Rounded (membundar)"
                    porosity = "porosity : 14-49%"
                    permeability = "permeability : Moderate "
                elif predictions['class1']   == "Sandstone (batupasir)":
                    warna = "warna : abu-abu, coklat, atau coklat kemerahan. Kadang juga berwarna putih, kuning, hijau, merah, ungu, oranye, hitam, dan lainnya."
                    ukuran = "ukuran butir : 1/256-1/16 milimeter"
                    kemas = "kemas : Tertutup"
                    sortasi = "sortasi : Baik"
                    bentuk = "Rounded (membundar)"
                    porosity = "porosity : 21-41%"
                    permeability = "permeability : Moderate "
                elif predictions['class1']   == "Siltstone (Batulanau)":
                    warna = "warna segar abu-abu, warna lapuk abu-abu kecoklatan."
                    ukuran = "< 1/256 milimeter"
                    kemas = "Tertutup"
                    sortasi = "Baik"
                    bentuk = "Rounded (membundar)"
                    porosity = "41-45%"
                    permeability = "Moderate "
                else:
                    warna = "-"
                    ukuran = "-"
                    kemas = "-"
                    sortasi = "-"
                    bentuk = "-"
                    porosity = "-"
                    permeability = "-"

            else:
                error = "Please upload images of jpg , jpeg and png extension only"

            if (len(error) == 0):
                return render_template('success.html', img=img, predictions=predictions, warna=warna, ukuran=ukuran, kemas=kemas, sortasi=sortasi, bentuk=bentuk, porosity=porosity, permeability=permeability)
            else:
                return render_template('tools.html', error=error)

    else:
        return render_template('tools.html')


if __name__ == "__main__":
    app.run(debug=True)

