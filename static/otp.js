document.addEventListener("DOMContentLoaded", function(){

/* ================= ELEMENTS ================= */
const inputs = document.querySelectorAll(".otp");
const msg = document.getElementById("msg");
const otpBox = document.getElementById("otpBox");
const timerEl = document.getElementById("timer");

let expired = false;

/* ================= AUTO FOCUS ================= */
if(inputs.length){
    inputs[0].focus();
}


/* ================= INPUT CONTROL ================= */
inputs.forEach((input,index)=>{

    // only number allow
    input.addEventListener("input",()=>{

        input.value = input.value.replace(/[^0-9]/g,'');

        // auto next
        if(input.value && index < inputs.length-1){
            inputs[index+1].focus();
        }
    });

    // backspace previous
    input.addEventListener("keydown",(e)=>{
        if(e.key==="Backspace" && input.value==="" && index>0){
            inputs[index-1].focus();
        }
    });
});


/* ================= PASTE OTP ================= */
otpBox.addEventListener("paste",(e)=>{
    e.preventDefault();

    let paste = (e.clipboardData || window.clipboardData)
        .getData("text")
        .replace(/\D/g,'');

    let digits = paste.split("");

    inputs.forEach((input,i)=>{
        input.value = digits[i] || "";
    });
});


/* ================= VERIFY OTP ================= */
window.verify = async function(){

    if(expired){
        msg.innerText="OTP expired. Login again.";
        msg.className="error";
        return;
    }

    let otp="";
    inputs.forEach(i=>otp+=i.value);

    if(otp.length!==6){
        msg.innerText="Enter full 6 digit OTP";
        msg.className="error";
        return;
    }

    const username = localStorage.getItem("otp_user");

    if(!username){
        msg.innerText="Session expired. Login again.";
        msg.className="error";
        return;
    }

    msg.innerText="Verifying...";

    try{

        const res = await fetch("/verify-otp",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            credentials:"include",    // ⭐⭐⭐ AUTO LOGOUT FIX
            body:JSON.stringify({username,otp})
        });

        const data = await res.json();

        if(res.status===200){

            msg.innerText="Login success ✔";
            msg.className="success";

            // otp user remove
            localStorage.removeItem("otp_user");

            setTimeout(()=>{
                window.location="/home";
            },900);

        }else{
            msg.innerText=data.detail || "Invalid OTP";
            msg.className="error";
        }

    }catch{
        msg.innerText="Server error";
        msg.className="error";
    }
};


/* ================= OTP TIMER ================= */

let time = 60;

function startTimer(){

    const interval = setInterval(()=>{

        let minutes = Math.floor(time/60);
        let seconds = time%60;

        seconds = seconds < 10 ? "0"+seconds : seconds;
        minutes = minutes < 10 ? "0"+minutes : minutes;

        timerEl.textContent = `${minutes}:${seconds}`;

        if(time <= 0){

            clearInterval(interval);
            expired = true;

            timerEl.textContent = "Expired";
            timerEl.style.color = "#ef4444";

            msg.innerText="OTP expired. Please login again.";
            msg.className="error";

            // disable inputs
            inputs.forEach(i=>i.disabled=true);
        }

        time--;

    },1000);
}

startTimer();

});
