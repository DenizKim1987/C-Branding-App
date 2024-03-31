도커 이미지 이름 : flask-selenium-app

코드수정 후 디플로이
docker build -t gcr.io/cbranding/flask-selenium-app:latest .

docker push gcr.io/cbranding/flask-selenium-app:latest

gcloud run deploy flask-selenium-app --image gcr.io/cbranding/flask-selenium-app:latest --platform managed --region asia-northeast3 --allow-unauthenticated
gcloud run deploy flask-selenium-app --image gcr.io/cbranding/flask-selenium-app:latest --memory '1Gi' --platform managed --region asia-northeast3 --allow-unauthenticated