import sys
import sqlite3
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QHeaderView, QApplication, QDialog
from Ecza1 import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.baglanti_olustur()
        self.LISTELE()
        
        self.btnEkle.clicked.connect(self.EKLE)
        self.btnSil.clicked.connect(self.SIL)
        self.btnAra.clicked.connect(self.ARA)
        self.btnGuncelle.clicked.connect(self.GUNCELLE)
        self.btnListele.clicked.connect(self.LISTELE)
        self.btnCikis.clicked.connect(self.CIKIS)
        self.menuHakkinda.triggered.connect(self.HAKKINDA)  
        self.tblwEczaList.itemSelectionChanged.connect(self.DOLDUR)
        
        self.penHakkinda = QDialog(self)
        self.penHakkinda.setWindowTitle("Hakkında")
        self.penHakkinda.setGeometry(100, 100, 400, 300)
        self.penHakkindaText = QtWidgets.QLabel(self.penHakkinda)
        self.penHakkindaText.setText("Bu uygulama Ecza Takip Sistemi içindir.")
        self.penHakkindaText.setGeometry(50, 50, 300, 200)

    def baglanti_olustur(self):
        try:
            self.conn = sqlite3.connect("veritaban.db", timeout=10)  
            self.curs = self.conn.cursor()
            self.sorguCreEczaList = """
                CREATE TABLE IF NOT EXISTS ecza (
                    Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    Barkot TEXT NOT NULL UNIQUE,
                    UrunAdi TEXT NOT NULL,
                    UrunFiyat TEXT NOT NULL,
                    Tarih TEXT NOT NULL,
                    Firma TEXT NOT NULL,
                    Adet INTEGER NOT NULL
                )
            """
            self.curs.execute(self.sorguCreEczaList)
            self.conn.commit()
        except sqlite3.Error as e:
            print("SQLite veritabanı hatası:", e) 
            
#--------------------------------EKLE------------------------------#
#------------------------------------------------------------------#
    def EKLE(self):
        try:
            _lneBarkot = self.lneBarkot.text()
            _lneUrunAdi = self.lneUrunAdi.text()
            _lneUrunFiyat = self.lneUrunFiyat.text()
            _dateTarih = self.dateTarih.date().toString(QtCore.Qt.ISODate)
            _cmbFirma = self.cmbFirma.currentText()
            _spnAdet = self.spnAdet.value()       
            self.curs.execute("INSERT INTO ecza (Barkot, UrunAdi, UrunFiyat, Tarih, Firma, Adet) VALUES (?, ?, ?, ?, ?, ?)", (_lneBarkot, _lneUrunAdi, _lneUrunFiyat, _dateTarih, _cmbFirma, _spnAdet))
            self.conn.commit()
            self.LISTELE()
        except sqlite3.Error as e:
            print("EKLE fonksiyonunda hata:", e)
            
#------------------------------LISTELE-----------------------------#
#------------------------------------------------------------------#
    def LISTELE(self):
        try:
            self.tblwEczaList.clear()
            self.tblwEczaList.setHorizontalHeaderLabels(('No', 'Barkot No', 'Ürün Adı', 'Ürün Fiyatı', 'Güncellenme Tarihi', 'Ürün Firması', 'Adet'))
            self.tblwEczaList.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.curs.execute("SELECT * FROM ecza")
            for satirIndeks, satirVeri in enumerate(self.curs):
                for sutunIndeks, sutunVeri in enumerate(satirVeri):
                    self.tblwEczaList.setItem(satirIndeks, sutunIndeks, QTableWidgetItem(str(sutunVeri)))
            self.temizle()
        except sqlite3.Error as e:
            print("LISTELE fonksiyonunda hata:", e)
            
#------------------------------temizle-----------------------------#
#------------------------------------------------------------------#
    def temizle(self):
        self.lneBarkot.clear()
        self.lneUrunAdi.clear()
        self.lneUrunFiyat.clear()
        self.cmbFirma.setCurrentIndex(-1)
        self.spnAdet.setValue(1)
        
#--------------------------------CIKIS-----------------------------#
#------------------------------------------------------------------#
    def CIKIS(self):
        cevap = QMessageBox.question(self, "ÇIKIŞ", "Programdan çıkmak istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            self.close()
        
#---------------------------------SIL------------------------------#
#------------------------------------------------------------------#
    def SIL(self):
        cevap = QMessageBox.question(self, "KAYIT SİL", "Kaydı silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            secili = self.tblwEczaList.selectedItems()
            silinecek = secili[1].text()
            try:
                self.curs.execute("DELETE FROM ecza WHERE Barkot=?", (silinecek,))
                self.conn.commit()
                self.LISTELE()
                self.statusbar.showMessage("KAYIT SİLME İŞLEMİ BAŞARIYLA GERÇEKLEŞTİ...", 10000)
            except sqlite3.Error as e:
                self.statusbar.showMessage("Şöyle bir hata ile karşılaşıldı: " + str(e))
        else:
            self.statusbar.showMessage("Silme işlemi iptal edildi...", 10000)
            
#--------------------------------ARA-------------------------------#
#------------------------------------------------------------------#
    def ARA(self):
        try:
            aranan1 = self.lneBarkot.text()
            aranan2 = self.lneUrunAdi.text()
            aranan3 = self.cmbFirma.currentText()
            self.curs.execute("SELECT * FROM ecza WHERE Barkot=? OR UrunAdi=? OR Firma=? OR (UrunAdi=? AND Firma=?)", (aranan1, aranan2, aranan3, aranan2, aranan3))
            self.conn.commit()
            self.tblwEczaList.clear()
            for satirIndeks, satirVeri in enumerate(self.curs):
                for sutunIndeks, sutunVeri in enumerate(satirVeri):
                    self.tblwEczaList.setItem(satirIndeks, sutunIndeks, QTableWidgetItem(str(sutunVeri)))
        except sqlite3.Error as e:
            print("ARA fonksiyonunda hata:", e)
            
#-------------------------------DOLDUR-----------------------------#
#------------------------------------------------------------------#
    def DOLDUR(self):
        secili = self.tblwEczaList.selectedItems()
        self.lneBarkot.setText(secili[1].text())
        self.lneUrunAdi.setText(secili[2].text())
        self.lneUrunFiyat.setText(secili[3].text())
        self.spnAdet.setValue(int(secili[6].text()))
        self.cmbFirma.setCurrentText(secili[5].text())
        yil, ay, gun = map(int, secili[4].text().split('-'))
        self.dateTarih.setDate(QtCore.QDate(yil, ay, gun))
        
#-------------------------------GUNCELLE-----------------------------#
#--------------------------------------------------------------------#
    def GUNCELLE(self):
        cevap = QMessageBox.question(self, "KAYIT GÜNCELLE", "Kaydı güncellemek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if cevap == QMessageBox.Yes:
            try:
                secili = self.tblwEczaList.selectedItems()
                _Id = int(secili[0].text())
                _lneBarkot = self.lneBarkot.text()
                _lneUrunAdi = self.lneUrunAdi.text()                                  
                _lneUrunFiyat = self.lneUrunFiyat.text()
                _dateTarih = self.dateTarih.date().toString(QtCore.Qt.ISODate)   
                _cmbFirma = self.cmbFirma.currentText()  
                _spnAdet = self.spnAdet.value()  
               
                self.curs.execute("UPDATE ecza SET Barkot=?, UrunAdi=?, UrunFiyat=?, Tarih=?, Firma=?, Adet=? WHERE Id=?", (_lneBarkot, _lneUrunAdi, _lneUrunFiyat, _dateTarih, _cmbFirma, _spnAdet, _Id))
                self.conn.commit()
                self.LISTELE()
            except sqlite3.Error as e:
                self.statusbar.showMessage("Şöyle bir hata meydana geldi: " + str(e))
        else:
            self.statusbar.showMessage("Güncelleme iptal edildi", 10000)

#-------------------------------Hakkinda-----------------------------#
#------------------------------------------------------------------#
    def HAKKINDA(self):
        self.penHakkinda.show()

if __name__ == "__main__":
    Uygulama = QApplication(sys.argv)
    penAna = MainWindow()
    penAna.show()
    sys.exit(Uygulama.exec_())
