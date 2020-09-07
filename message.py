import datetime
from dateutil.relativedelta import relativedelta
import calendar
import math


def liczba_dni_w_miesiacu(data): #ta funkcja jest niepotrzebna, mimo ze baza wynosi 365 dni, to do accruowania bank liczu=y 366 dni dla roku przestepnego
    if calendar.monthrange(data.year, data.month)[1] == 29:
        return 29 # zmienilem na 29,zeby spr czy policzy tak jak apka -
        # nalezy usunac funkcje i pozwolic liczyc 29 dni dla roku przestepnego
    else:
        return calendar.monthrange(data.year, data.month)[1]


def round_up(n, decimals=2):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


class KredytBaza:
    def __init__(self, kwota_kredytu, marza_banku, wibor, ilosc_okresow_rozliczeniowych, rok_kredyt, miesiac_kredyt, dzien_kredyt):
        self.kwota_kredytu = kwota_kredytu
        self.marza_banku = marza_banku
        self.wibor = wibor
        self.ilosc_okresow_rozliczeniowych = ilosc_okresow_rozliczeniowych
        self.dzien_kredyt = dzien_kredyt
        self.miesiac_kredyt = miesiac_kredyt
        self.rok_kredyt = rok_kredyt

        self.data_wziecia_kredytu = datetime.date(self.rok_kredyt, self.miesiac_kredyt, self.dzien_kredyt)
        self.koniec_kredytu = self.data_wziecia_kredytu + relativedelta(months=ilosc_okresow_rozliczeniowych)
        self.oprcentowanie_roczne = (self.marza_banku + self.wibor)/100
        self.oprcentowanie_roczne = round(self.oprcentowanie_roczne, 6)
        self.wspolczynnik_q = round((1 + self.oprcentowanie_roczne / 12), 6)
        self.nadplatyyy = {}
        self.dodane_okresy = False
        self.rata = 1
        self.zrealizowane_nadplaty = {}
        self.saldo_zadluzenia = self.kwota_kredytu
        self.data_aktualnego_rozliczenia = self.data_wziecia_kredytu
        self.skrocone_okresy_kredytowania = 0
        self.suma_splaconego_kapitalu = 0
        self.okresy_pozostale_do_splaty = self.ilosc_okresow_rozliczeniowych

    def wysokosc_raty(self):
        wysokosc_raty = self.kwota_kredytu * (self.wspolczynnik_q ** self.ilosc_okresow_rozliczeniowych) * (
                self.wspolczynnik_q - 1) / ((self.wspolczynnik_q ** self.ilosc_okresow_rozliczeniowych) - 1)
        return round_up(wysokosc_raty, decimals=2)

    def wylicz_kapital(self):

        czesc_odsetkowa = round((self.saldo_zadluzenia * self.oprcentowanie_roczne / 365 * liczba_dni_w_miesiacu(self.data_aktualnego_rozliczenia)), 2)
        czesc_kapitalowa = round((self.wysokosc_raty() - czesc_odsetkowa), 2)
        return czesc_kapitalowa
# *************************************************************************************
    def wykonaj_nadplaty(self, wylicz_kapital_param):

        skrocone_okresy_kredytowania = 0
        if len(self.nadplatyyy) > 0: # sprawdzam czy sa jeszcze nadplaty w dict
            kiedy = sorted(self.nadplatyyy)
        else:
            return
        if self.rata == kiedy[0]:
            z = kiedy[0]
            wartosc_nadplaty = self.nadplatyyy[kiedy[0]]

            while wartosc_nadplaty > wylicz_kapital_param:
                wartosc_nadplaty -= wylicz_kapital_param
                self.suma_splaconego_kapitalu += round(wylicz_kapital_param, 2)
                skrocone_okresy_kredytowania += 1
                self.saldo_zadluzenia -= wylicz_kapital_param
                self.wylicz_kapital()
                continue
        else:
            return
        if wartosc_nadplaty < wylicz_kapital_param:
            niepelna_rata = round_up(wartosc_nadplaty, decimals=2)
            self.saldo_zadluzenia -= niepelna_rata
            self.suma_splaconego_kapitalu += niepelna_rata
            # self.nadplatyyy[""]  stworzyc dictionary dla przechowywania informacji
            # o kazdym nadplacaonym okresie - ile kapitalu, odsetek
        if len(kiedy) > 1:
            okres = self.nadplatyyy.pop(z)
        else:
            okres = self.nadplatyyy.pop(z)
        self.okresy_pozostale_do_splaty -= skrocone_okresy_kredytowania
        self.skrocone_okresy_kredytowania += skrocone_okresy_kredytowania

        print(self.saldo_zadluzenia)
        return print(f"Naplata w wysokosci {okres} spowodowala skrocenie czasu kredytowania o {skrocone_okresy_kredytowania} rat/y. Niepelna czesc kapitalowa w wysokosci {niepelna_rata} zł obnizyla kapital ")

# *************************************************************************************

    def nadplata_kiedy(self):  # tworze dict dotyczaca nadplat
        pytanie = input("czy chcesz nadplacac kredyt [tak/nie]: ")
        if pytanie == "tak":
            while pytanie:
                okres = input("dodaj rate przed ktora chcesz zrobic nadplate: ")
                kwota = input(f"dodaj kwote dla nadplaty przed {okres} ratą: ")
                pytanie = input("czy chcesz dodac kolejna naplaty [tak/nie]: ")
                self.nadplatyyy[int(okres)] = int(kwota)
                if pytanie == "tak":
                    continue
                elif pytanie == "nie":
                    self.dodane_okresy = True
                    return self.nadplatyyy
        elif pytanie == "nie":
            print("Kredyt nie bedzie nadplacany")

    def kapital_odsetki(self):
        if not self.dodane_okresy:
            self.nadplata_kiedy()

        suma_splaconych_odsetek = 0

        miesiace = {
            1: "Styczeń",
            2: "Luty",
            3: "Marzec",
            4: "Kwiecień",
            5: "Maj",
            6: "Czerwiec",
            7: "Lipiec",
            8: "Sierpień",
            9: "wrzesień",
            10: "Październik",
            11: "Listopad",
            12: "Grudzień"
        }
        self.saldo_zadluzenia = self.kwota_kredytu

        while self.okresy_pozostale_do_splaty > 0:
            if self.okresy_pozostale_do_splaty == 1:
                if self.saldo_zadluzenia > self.rata:
                    platnosc_za_miesiac = self.data_aktualnego_rozliczenia.month
                    czesc_odsetkowa = round((self.saldo_zadluzenia * self.oprcentowanie_roczne / 365 * liczba_dni_w_miesiacu(self.data_aktualnego_rozliczenia)), 2)
                    czesc_kapitalowa = round((self.wysokosc_raty() - czesc_odsetkowa), 2)

                    self.saldo_zadluzenia -= czesc_kapitalowa
                    wysokosc_ost_raty = round_up((self.wysokosc_raty() + round(self.saldo_zadluzenia, 2)), decimals=1)
                    czesc_kapitalowa = round((wysokosc_ost_raty - czesc_odsetkowa), 2)
                    self.suma_splaconego_kapitalu += round(czesc_kapitalowa, 2)
                    suma_splaconych_odsetek += round(czesc_odsetkowa, 2)
                    self.okresy_pozostale_do_splaty -= 1

                elif self.saldo_zadluzenia < self.rata:

                    platnosc_za_miesiac = self.data_aktualnego_rozliczenia.month #wysokosc_ost_raty = round_up((self.wysokosc_raty() + round(self.saldo_zadluzenia, 2)), decimals=1)
                    wysokosc_ost_raty = round_up(self.saldo_zadluzenia, decimals= 1)
                    czesc_odsetkowa = round((wysokosc_ost_raty * self.oprcentowanie_roczne / 365 * liczba_dni_w_miesiacu(self.data_aktualnego_rozliczenia)), 2)
                    czesc_kapitalowa = round(self.saldo_zadluzenia, 2)
                    self.saldo_zadluzenia -= self.saldo_zadluzenia
                    # wysokosc_ost_raty = round_up((self.wysokosc_raty() + round(self.saldo_zadluzenia, 2)), decimals=1)
                    # czesc_kapitalowa = round((wysokosc_ost_raty - czesc_odsetkowa), 2)
                    self.suma_splaconego_kapitalu += round(czesc_kapitalowa, 2)
                    suma_splaconych_odsetek += round(czesc_odsetkowa, 2)
                    self.okresy_pozostale_do_splaty -= 1
                    # print(f"Wysokośc ostatniej raty wynosi {wysokosc_ost_raty} zł")
                    print("****splacana ostatnia rata - wysokosc salda zadluzenia jest mnijesza niz wyokosc raty")

                print("\n\n----------------------------------------------------------")
                print(f"Platnosc raty za miesiac {miesiace.get(platnosc_za_miesiac)} wypada {self.data_aktualnego_rozliczenia + relativedelta(months=+1)}")
                print(f"W tym miesiacu odsetki naliczane sa dla: {liczba_dni_w_miesiacu(self.data_aktualnego_rozliczenia)} dni")
                print(f"Jest to ostatnia rata. Zostanie ona powiększona o pozostałą część kapitałową w wysokości: {round(self.saldo_zadluzenia, 2)} zł")
                print(f"Wysokośc ostatniej raty wynosi {wysokosc_ost_raty} zł")
                print(f"Jej czesc kapitalowa stanowi {round(czesc_kapitalowa, 2)} zł.")
                print(f"Jej czesc odsetkowa stanowi {czesc_odsetkowa} zł.")
                print("----------------------------------------------------------")

            else:
                if self.dodane_okresy:
                    self.wykonaj_nadplaty(self.wylicz_kapital())

                platnosc_za_miesiac = self.data_aktualnego_rozliczenia.month

                czesc_odsetkowa = round((self.saldo_zadluzenia * self.oprcentowanie_roczne / 365 * liczba_dni_w_miesiacu(self.data_aktualnego_rozliczenia)), 2)
                czesc_kapitalowa = round((self.wysokosc_raty() - czesc_odsetkowa), 2)

                print("\n\n----------------------------------------------------------")
                print(f"***test druk okresy_pozostale_do_splaty {self.okresy_pozostale_do_splaty}")
                print(f"Platnosc raty za miesiac {miesiace.get(platnosc_za_miesiac)} wypada {self.data_aktualnego_rozliczenia + relativedelta(months=+1)}")
                print(f"W tym miesiacu odsetki naliczane sa dla: {liczba_dni_w_miesiacu(self.data_aktualnego_rozliczenia)} dni")
                print(f"Jest to {self.rata} rata. Pozostanie {self.okresy_pozostale_do_splaty - 1} rat do spłaty")
                print(f"Twoja rata wynosi {self.wysokosc_raty()} zł")
                print(f"Jej czesc kapitalowa stanowi {czesc_kapitalowa} zł.")
                print(f"Jej czesc odsetkowa stanowi {czesc_odsetkowa} zł.")
                print("----------------------------------------------------------")


                self.suma_splaconego_kapitalu += round(czesc_kapitalowa,2)
                suma_splaconych_odsetek += round(czesc_odsetkowa, 2)
                self.saldo_zadluzenia -= czesc_kapitalowa
                self.rata += 1
                self.data_aktualnego_rozliczenia += relativedelta(months=+1)
                self.okresy_pozostale_do_splaty -= 1
                print(f"***Testowe pokazywanie {self.saldo_zadluzenia} zl")

        print(f"\nLacznie splacono kapital w wysokosci {round(self.suma_splaconego_kapitalu,2)}. Kilka groszy roznicy w kapitale wynika z zaokraglania ostanitej raty")
        print(f"Lacznie splacono odsetki w wysokosci {round(suma_splaconych_odsetek, 2)}")
        print("\n----------------------------------------------------------")


kredyt_1 = KredytBaza(325000, 2.14, 0, 360, 2020, 8, 5)


kredyt_1.kapital_odsetki()