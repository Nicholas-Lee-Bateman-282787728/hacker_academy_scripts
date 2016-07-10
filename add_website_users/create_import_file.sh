curl -O https://www.hackeracademy.org/users.xls
libreoffice --convert-to csv users.xls
python wui.py users.csv
