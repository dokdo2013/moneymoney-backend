# Moneymoney Backend
가계부 관리를 위한 지출내역 등록 Backend (Google Spreadsheet, Google OTP 연동)

## Tech Stack
- Serverless Framework
- Python 3.8
- Flask
- AWS Lambda

## Relational Links
- [Frontend Git Repo](https://github.com/dokdo2013/moneymoney-front)
- [Website](https://money.haenu.com)

## Project Usage
### Environment Requirements
- Node.js & NPM
- Python 3.8^
- Docker

### Shell
Project Install and Deploy Script
```bash
npm install -g serverless
npm install
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
serverless deploy
deactivate
```

Deploy to Production
```bash
sls deploy --stage v1 --region ap-northeast-2
```

