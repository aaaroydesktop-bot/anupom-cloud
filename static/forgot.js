const msg=document.getElementById("msg");

async function sendOtp(){

    const email=document.getElementById("email").value.trim();

    if(!email){
        msg.innerText="Enter your email!";
        msg.className="error";
        return;
    }

    msg.innerText="Sending OTP...";

    try{

        let res=await fetch("/forgot-password",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({email:email})
        });

        let data=await res.json();

        if(res.status===200){

            msg.className="success";
            msg.innerText="OTP sent to your email ✔";

            // store email for reset page
            localStorage.setItem("reset_email",email);

            setTimeout(()=>{
                window.location="/reset";
            },1000);

        }else{
            msg.className="error";
            msg.innerText=data.detail;
        }

    }catch{
        msg.className="error";
        msg.innerText="Server not responding";
    }
}
