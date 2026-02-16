const msg=document.getElementById("msg");

async function resetPass(){

    const email = localStorage.getItem("reset_email");
    const otp = document.getElementById("otp").value.trim();
    const new_password = document.getElementById("password").value.trim();

    if(!email){
        msg.innerText="Session expired. Go to forgot page again.";
        msg.className="error";
        return;
    }

    if(otp.length !== 6){
        msg.innerText="Enter valid 6 digit OTP";
        msg.className="error";
        return;
    }

    if(new_password.length < 4){
        msg.innerText="Password must be at least 4 characters";
        msg.className="error";
        return;
    }

    msg.innerText="Changing password...";

    try{

        let res = await fetch("/reset-password",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({
                email:email,
                otp:otp,
                new_password:new_password
            })
        });

        let data = await res.json();

        if(res.status===200){
            msg.className="success";
            msg.innerText="Password changed successfully ✔";

            localStorage.removeItem("reset_email");

            setTimeout(()=>{
                window.location="/login";
            },1500);

        }else{
            msg.className="error";
            msg.innerText=data.detail;
        }

    }catch{
        msg.className="error";
        msg.innerText="Server error";
    }
}
