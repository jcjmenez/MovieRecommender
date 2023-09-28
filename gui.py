from PyQt5.QtWidgets import QTabWidget, QMainWindow, QApplication, QPlainTextEdit, QPushButton, QLabel, QTableWidget, QFileDialog, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5 import uic

import sys
from PyQt5.QtWidgets import QApplication
import requests
import recommender
import scraping
from predicter import predict_from_user

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("interfaces/MainWindow.ui", self)
        
        self.setWindowIcon(QIcon('assets/icon.png'))
        self.setWindowTitle("Proyecto - SSII")
        
        self.tab_widget = self.findChild(QTabWidget, "tabWidget")
        self.tab_widget.setTabText(0, "Recomendacion")
        self.tab_widget.setTabText(1, "Predecir valoracion")
        self.tab_widget.setTabText(2, "Predecir N Peliculas")
        
        # Recomendacion
        self.search_icon = self.findChild(QPushButton, "pushButton") 
        self.image = self.findChild(QLabel, "label_5")
        self.image1 = self.findChild(QLabel, "label_6")
        self.image2 = self.findChild(QLabel, "label_7")
        self.image3 = self.findChild(QLabel, "label_8")
        self.image4 = self.findChild(QLabel, "label_9")
        self.title1 = self.findChild(QLabel, "label_2")
        self.title2 = self.findChild(QLabel, "label_4")
        self.title3 = self.findChild(QLabel, "label_19")
        self.title4 = self.findChild(QLabel, "label_20")
        self.title5 = self.findChild(QLabel, "label_21")
        self.loader = self.findChild(QLabel, "loader")
        self.text_edit = self.findChild(QPlainTextEdit, "plainTextEdit")

        self.search_icon.clicked.connect(lambda: self.search())


        # Predecir valoracion
        self.path_single_movie_qte = self.findChild(QPlainTextEdit, "plainTextEdit_4")
        self.user_path_btn2 = self.findChild(QPushButton, "pushButton_5") 
        self.user_movie_qte = self.findChild(QPlainTextEdit, "plainTextEdit_2")
        self.user_predict = self.findChild(QPushButton, "pushButton_6") 
        self.result_pred = self.findChild(QLabel, "label_10")

        self.user_path_btn2.clicked.connect(lambda: self.select_file(self.path_single_movie_qte))
        self.user_predict.clicked.connect(lambda: self.predict_by_movie(self.path_single_movie_qte.toPlainText(), self.user_movie_qte.toPlainText()))

        # Predecir N Peliculas
        self.table = self.findChild(QTableWidget, "tableWidget")
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.predict_btn = self.findChild(QPushButton, "pushButton_3")
        self.user_path_qte = self.findChild(QPlainTextEdit, "plainTextEdit_3")
        self.number_of_pred = self.findChild(QPlainTextEdit, "plainTextEdit_5")
        self.user_path_btn = self.findChild(QPushButton, "pushButton_4")
        self.user_path_btn.clicked.connect(lambda: self.select_file(self.user_path_qte))
        self.predict_btn.clicked.connect(lambda: self.predict(self.user_path_qte.toPlainText(), self.number_of_pred.toPlainText()))

        self.show()



    def predict_by_movie(self, path, user_input_title):
        predictions = predict_from_user(path)
        titles_list = predictions["name"]
        found_titles = []
        print(user_input_title)
        for title in titles_list:
            if user_input_title.lower() in title.split(" (")[0].lower():
                found_titles.append(title)
            
        scores_list = predictions["score"]
        idx = 0
        print(found_titles)
        for i in range(len(titles_list)):
            if len(found_titles) <= 0:
                self.result_pred.setText("Ya has valorado esta pelicula")
            else:
                if titles_list[i] == found_titles[0]:
                    idx = i
                    pred_for_movie = scores_list[idx]
                    text = "Prediccion para " + found_titles[0] + ": " + str(pred_for_movie)
                    self.result_pred.setText(text)


    def predict(self, path, num_of_pred):
        int_number_of_pred = 20
        try:
            int_number_of_pred = int(num_of_pred)
        except:
            int_number_of_pred = 20
        while self.table.rowCount() > 0:
            self.table.removeRow(0)
        predictions = predict_from_user(path)
        titles_list = predictions["name"]
        scores_list = predictions["score"]

        # idx = 0
        # for i in range(len(titles_list)):
        #     if titles_list[i] == iptmovie:
        #         idx = i
        # pred_for_movie = scores_list[idx]

        for i in range(int_number_of_pred):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(titles_list[i])))
            self.table.setItem(i, 1, QTableWidgetItem(str(scores_list[i])))


    def select_file(self, qte):
        file = QFileDialog.getOpenFileName(self, "Open file")[0]
        if file:
            qte.setPlainText(file)

    def search(self):
        links=[]
        user_movie = self.text_edit.toPlainText()
        print(user_movie)
        movies_list = recommender.recommendations(str(user_movie), 5)
        print(movies_list)
        for movie in movies_list:
            movie_id = movie[0]
            imdb_id = scraping.get_imdb_id(movie)
            image_url = scraping.get_image_from_id(str(imdb_id))
            links.append({"url":str(image_url), "title":movie})
        
        self.show_images(links)

    def show_images(self, links):
            images = []
            for link in links:
                image = QImage()
                image.loadFromData(requests.get(link["url"]).content)
                images.append({"img":image, "title":link["title"]})

            pmax = QPixmap(images[0]["img"])
            self.image.setPixmap(pmax)
            self.image.setScaledContents(True)
            self.title1.setText(images[0]['title'])
            pmax = QPixmap(images[1]["img"])
            self.image1.setPixmap(pmax)
            self.image1.setScaledContents(True)
            self.title2.setText(images[1]['title'])
            pmax = QPixmap(images[2]["img"])
            self.image2.setPixmap(pmax)
            self.image2.setScaledContents(True)
            self.title3.setText(images[2]['title'])
            pmax = QPixmap(images[3]["img"])
            self.image3.setPixmap(pmax)
            self.image3.setScaledContents(True)
            self.title4.setText(images[3]['title'])
            pmax = QPixmap(images[4]["img"])
            self.image4.setPixmap(pmax)
            self.image4.setScaledContents(True)
            self.title5.setText(images[4]['title'])


            

          


if (__name__ == '__main__'):
    app = QApplication(sys.argv)
    UIWindow = UI()
    app.exec_()


