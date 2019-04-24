const dgram = require('dgram');
const express = require('express');
const ip = require('ip');
const multer = require('multer');
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/') // cb 콜백함수를 통해 전송된 파일 저장 디렉토리 설정
    },
    filename: function (req, file, cb) {
        cb(null, file.originalname) // cb 콜백함수를 통해 전송된 파일 이름 설정
    }
});
const upload = multer({ storage: storage });

const app = express();
app.post('/upload', upload.single('userfile'), function(req, res){
    res.send('Uploaded! : '+req.file); // object를 리턴함
    console.log(req.file); // 콘솔(터미널)을 통해서 req.file Object 내용 확인 가능.
});

app.listen(3000, function(){
    console.log("Express server has started on port 3000")
});

const serverConfig = {
    "service" : "cSync",
    "ip" : ip.address(),
    "port" : 3000
};
const client = dgram.createSocket("udp4");
const message = JSON.stringify(serverConfig);
client.send(message, 0, message.length, 8000, "192.168.0.255");
