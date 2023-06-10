# honeywell-tcc-exporter

 sudo docker build . -t myevo && sudo docker run -e TCC_CONFIGOP="stats" -e TCC_USERNAME="myusername" -e TCC_PASSWORD="mypassword" -p 9999:9999 myevo