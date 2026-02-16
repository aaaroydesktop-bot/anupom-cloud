// ================= GLOBAL =================

let currentPage = "send";
let lastFileCount = 0;


// ================= PAGE CONTROLLER =================

function openPage(pageId){

    document.querySelectorAll(".page").forEach(page=>{
        page.classList.remove("active");
    });

    const target=document.getElementById(pageId);
    if(target){
        target.classList.add("active");
    }
}


// ================= SEND PAGE =================

function showSend(){
    currentPage="send";
    openPage("sendPage");
}


// ================= INBOX =================

function loadInbox(){

    currentPage="inbox";
    openPage("inboxPage");

    fetch("/inbox")
    .then(res=>res.json())
    .then(data=>{

        const list=document.getElementById("inboxList");
        list.innerHTML="";

        lastFileCount=data.length;

        if(data.length===0){
            list.innerHTML="<p>No files received yet.</p>";
            return;
        }

        data.forEach(f=>{

            let div=document.createElement("div");
            div.className="fileItem";

            let downloadBtn=`<br>
            <a href="${f.link}" class="downloadBtn" download>⬇ Download</a>`;

            let preview="";

            if(f.type==="image"){
                preview=`<img src="${f.link}" class="previewImg">${downloadBtn}`;
            }
            else if(f.type==="video"){
                preview=`
                <video controls class="previewVideo">
                    <source src="${f.link}">
                </video>
                ${downloadBtn}`;
            }
            else if(f.type==="pdf"){
                preview=`<a href="${f.link}" target="_blank" class="viewBtn">📄 View PDF</a>${downloadBtn}`;
            }
            else{
                preview=downloadBtn;
            }

            div.innerHTML=`
            <div>
                <b>From:</b> ${f.sender}<br>
                ${preview}
                <div class="expireTag">⏳ Expires in ${f.expires} day(s)</div>
            </div>
            `;

            list.appendChild(div);
        });

    });
}


// ================= MY FILES =================

function loadMyFiles(){

    currentPage="myfiles";
    openPage("myfilesPage");

    fetch("/my-files")
    .then(res=>res.json())
    .then(data=>{

        const list=document.getElementById("myFilesList");
        list.innerHTML="";

        if(data.length===0){
            list.innerHTML="<p>You have not sent any files yet.</p>";
            return;
        }

        data.forEach(f=>{

            let div=document.createElement("div");
            div.className="fileItem";

            div.innerHTML=`
            <div>
                <b>To:</b> ${f.receiver}<br>
                <a href="${f.link}" class="downloadBtn" download>⬇ Download</a>
            </div>
            `;

            list.appendChild(div);
        });

    });
}


// ================= SEND FILE =================

function sendFile(){

    let file=document.getElementById("fileInput").files[0];
    let receiver=document.getElementById("receiverEmail").value;

    if(!file){
        alert("Please select a file!");
        return;
    }

    if(receiver.trim()===""){
        alert("Enter receiver email!");
        return;
    }

    document.getElementById("progressBar").style.width="0%";
    document.getElementById("uploadStatus").innerText="Preparing upload...";

    let formData=new FormData();
    formData.append("file",file);
    formData.append("receiver",receiver);

    let xhr=new XMLHttpRequest();
    xhr.open("POST","/send-file",true);

    xhr.upload.onprogress=function(e){
        if(e.lengthComputable){
            let percent=(e.loaded/e.total)*100;
            document.getElementById("progressBar").style.width=percent+"%";
            document.getElementById("uploadStatus").innerText=
            "Uploading: "+Math.floor(percent)+"%";
        }
    };

    xhr.onload=function(){
        if(xhr.status===200){
            document.getElementById("uploadStatus").innerText="✅ File Sent Successfully!";
            document.getElementById("fileInput").value="";
        }else{
            document.getElementById("uploadStatus").innerText="❌ Upload failed!";
        }
    };

    xhr.onerror=function(){
        document.getElementById("uploadStatus").innerText="❌ Network Error!";
    };

    xhr.send(formData);
}


// ================= SMART AUTO REFRESH =================

setInterval(()=>{

    if(currentPage!=="inbox") return;

    fetch("/inbox")
    .then(res=>res.json())
    .then(data=>{
        if(data.length!==lastFileCount){
            loadInbox();
        }
    })
    .catch(()=>{});

},5000);
