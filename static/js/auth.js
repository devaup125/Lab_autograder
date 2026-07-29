/* ==========================================================
   LAB AUTO GRADER
   Authentication JavaScript
   Part 1
   ========================================================== */

"use strict";

/* ==========================================================
   GLOBAL OBJECT
   ========================================================== */

const Auth = {

    currentRole: "student",

    darkMode: false,

    rememberMe: false,

    isLoading: false,

    otpTimer: null,

    otpSeconds: 60,

    storage: window.localStorage

};

/* ==========================================================
   DOM READY
   ========================================================== */

document.addEventListener("DOMContentLoaded", () => {

    initializeApp();

});

/* ==========================================================
   INITIALIZATION
   ========================================================== */

function initializeApp(){

    cacheElements();

    bindEvents();

    restoreTheme();

    restoreRole();

    restoreRememberMe();

}

/* ==========================================================
   CACHE DOM
   ========================================================== */

let elements = {};

function cacheElements(){

    elements.loginForm =
        document.getElementById("loginForm");

    elements.email =
        document.getElementById("email");

    elements.password =
        document.getElementById("password");

    elements.loginButton =
        document.getElementById("loginBtn");

    elements.remember =
        document.getElementById("rememberMe");

    elements.toastContainer =
        document.getElementById("toastContainer");

    elements.themeToggle =
        document.getElementById("themeToggle");

}

/* ==========================================================
   EVENT LISTENERS
   ========================================================== */

function bindEvents(){

    if(elements.loginForm){

        elements.loginForm.addEventListener(
            "submit",
            loginHandler
        );

    }

    if(elements.themeToggle){

        elements.themeToggle.addEventListener(
            "click",
            toggleTheme
        );

    }

}

/* ==========================================================
   UTILITIES
   ========================================================== */

function $(selector){

    return document.querySelector(selector);

}

function $$(selector){

    return document.querySelectorAll(selector);

}

function byId(id){

    return document.getElementById(id);

}

function show(element){

    if(element){

        element.style.display = "";

    }

}

function hide(element){

    if(element){

        element.style.display = "none";

    }

}

function enable(element){

    if(element){

        element.disabled = false;

    }

}

function disable(element){

    if(element){

        element.disabled = true;

    }

}

/* ==========================================================
   CLASS HELPERS
   ========================================================== */

function addClass(element,className){

    if(element){

        element.classList.add(className);

    }

}

function removeClass(element,className){

    if(element){

        element.classList.remove(className);

    }

}

function toggleClass(element,className){

    if(element){

        element.classList.toggle(className);

    }

}

/* ==========================================================
   TOAST SYSTEM
   ========================================================== */

function showToast(

    title,

    message,

    type="info"

){

    if(!elements.toastContainer){

        console.log(title,message);

        return;

    }

    const toast=document.createElement("div");

    toast.className=`login-toast toast-${type}`;

    toast.innerHTML=`

        <div class="toast-header">

            <strong>${title}</strong>

            <button class="btn-close"></button>

        </div>

        <div class="toast-body">

            ${message}

        </div>

    `;

    elements.toastContainer.appendChild(toast);

    const closeButton=

        toast.querySelector(".btn-close");

    if(closeButton){

        closeButton.onclick=()=>{

            toast.remove();

        };

    }

    setTimeout(()=>{

        toast.remove();

    },5000);

}

/* ==========================================================
   ALERT SYSTEM
   ========================================================== */

function showAlert(

    target,

    message,

    type="danger"

){

    if(!target) return;

    target.innerHTML=

    `<div class="login-alert alert-${type}">

        ${message}

    </div>`;

}

function clearAlert(target){

    if(target){

        target.innerHTML="";

    }

}

/* ==========================================================
   LOADING
   ========================================================== */

function setLoading(state){

    Auth.isLoading=state;

    if(!elements.loginButton) return;

    if(state){

        disable(elements.loginButton);

        elements.loginButton.innerHTML=

        `<span class="spinner"></span>

         Signing In...`;

    }

    else{

        enable(elements.loginButton);

        elements.loginButton.innerHTML=

        `Sign In`;

    }

}

/* ==========================================================
   LOCAL STORAGE
   ========================================================== */

function save(key,value){

    Auth.storage.setItem(

        key,

        JSON.stringify(value)

    );

}

function load(key){

    const value=

        Auth.storage.getItem(key);

    if(!value) return null;

    return JSON.parse(value);

}

function remove(key){

    Auth.storage.removeItem(key);

}

/* ==========================================================
   THEME
   ========================================================== */

function toggleTheme(){

    document.body.classList.toggle("dark-mode");

    Auth.darkMode=

        document.body.classList.contains("dark-mode");

    save(

        "theme",

        Auth.darkMode

    );

}

function restoreTheme(){

    const theme=

        load("theme");

    if(theme){

        document.body.classList.add("dark-mode");

        Auth.darkMode=true;

    }

}

/* ==========================================================
   PLACEHOLDERS
   ========================================================== */

function restoreRole(){}

function restoreRememberMe(){}

function loginHandler(event){

    event.preventDefault();

}
/* ==========================================================
   PART 2
   EMAIL VALIDATION • PASSWORD VALIDATION
   REMEMBER ME • PASSWORD TOGGLE
   ========================================================== */

/* ==========================================================
   EMAIL VALIDATION
   ========================================================== */

function validateEmail(email){

    const regex =

        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return regex.test(

        String(email).trim()

    );

}

/* ==========================================================
   PASSWORD VALIDATION
   ========================================================== */

function validatePassword(password){

    return password.length >= 8;

}

function passwordStrength(password){

    let score = 0;

    if(password.length >= 8) score++;

    if(/[A-Z]/.test(password)) score++;

    if(/[a-z]/.test(password)) score++;

    if(/[0-9]/.test(password)) score++;

    if(/[^A-Za-z0-9]/.test(password)) score++;

    return score;

}

/* ==========================================================
   UPDATE PASSWORD STRENGTH UI
   ========================================================== */

function updatePasswordStrength(password){

    const bar =

        byId("strengthFill");

    const text =

        byId("strengthText");

    if(!bar || !text) return;

    bar.className = "strength-fill";

    const strength =

        passwordStrength(password);

    switch(strength){

        case 0:
        case 1:

            bar.classList.add(
                "strength-weak"
            );

            text.textContent =
                "Weak";

            break;

        case 2:

            bar.classList.add(
                "strength-fair"
            );

            text.textContent =
                "Fair";

            break;

        case 3:
        case 4:

            bar.classList.add(
                "strength-good"
            );

            text.textContent =
                "Good";

            break;

        default:

            bar.classList.add(
                "strength-strong"
            );

            text.textContent =
                "Strong";

    }

}

/* ==========================================================
   SHOW / HIDE PASSWORD
   ========================================================== */

function togglePassword(){

    if(!elements.password) return;

    const icon =

        byId("togglePassword");

    if(elements.password.type === "password"){

        elements.password.type = "text";

        if(icon){

            icon.classList.remove("fa-eye");

            icon.classList.add("fa-eye-slash");

        }

    }

    else{

        elements.password.type = "password";

        if(icon){

            icon.classList.remove("fa-eye-slash");

            icon.classList.add("fa-eye");

        }

    }

}

/* ==========================================================
   REMEMBER ME
   ========================================================== */

function restoreRememberMe(){

    const saved =

        load("rememberMe");

    if(saved){

        Auth.rememberMe = true;

        if(elements.remember){

            elements.remember.checked = true;

        }

        const email =

            load("savedEmail");

        if(email && elements.email){

            elements.email.value = email;

        }

    }

}

function saveRememberMe(){

    if(!elements.remember) return;

    if(elements.remember.checked){

        save(

            "rememberMe",

            true

        );

        save(

            "savedEmail",

            elements.email.value

        );

    }

    else{

        remove("rememberMe");

        remove("savedEmail");

    }

}

/* ==========================================================
   FORM VALIDATION
   ========================================================== */

function validateLoginForm(){

    let valid = true;

    if(!validateEmail(

        elements.email.value

    )){

        markInvalid(

            elements.email,

            "Invalid email address"

        );

        valid = false;

    }

    else{

        markValid(

            elements.email

        );

    }

    if(!validatePassword(

        elements.password.value

    )){

        markInvalid(

            elements.password,

            "Minimum 8 characters"

        );

        valid = false;

    }

    else{

        markValid(

            elements.password

        );

    }

    return valid;

}

/* ==========================================================
   INPUT STATE
   ========================================================== */

function markValid(input){

    input.classList.remove(

        "is-invalid"

    );

    input.classList.add(

        "is-valid"

    );

}

function markInvalid(

    input,

    message

){

    input.classList.remove(

        "is-valid"

    );

    input.classList.add(

        "is-invalid"

    );

    const feedback =

        input.parentElement.querySelector(

            ".invalid-feedback"

        );

    if(feedback){

        feedback.textContent =

            message;

    }

}

/* ==========================================================
   LIVE VALIDATION
   ========================================================== */

function attachValidation(){

    if(elements.email){

        elements.email.addEventListener(

            "input",

            ()=>{

                if(validateEmail(

                    elements.email.value

                )){

                    markValid(

                        elements.email

                    );

                }

            }

        );

    }

    if(elements.password){

        elements.password.addEventListener(

            "input",

            ()=>{

                updatePasswordStrength(

                    elements.password.value

                );

                if(validatePassword(

                    elements.password.value

                )){

                    markValid(

                        elements.password

                    );

                }

            }

        );

    }

}

/* ==========================================================
   EXTRA EVENTS
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        attachValidation();

        const toggle =

            byId("togglePassword");

        if(toggle){

            toggle.addEventListener(

                "click",

                togglePassword

            );

        }

    }

);
/* ==========================================================
   PART 3
   ROLE SELECTION • LOGIN SUBMISSION
   FETCH API • REDIRECT • ERROR HANDLING
   ========================================================== */

/* ==========================================================
   ROLE SELECTION
   ========================================================== */

function initializeRoleSelection(){

    const roles = document.querySelectorAll(".role-option");

    if(!roles.length) return;

    roles.forEach(role=>{

        role.addEventListener("click",()=>{

            roles.forEach(item=>{

                item.classList.remove("active");

            });

            role.classList.add("active");

            Auth.currentRole = role.dataset.role;

            save("selectedRole",Auth.currentRole);

        });

    });

}

function restoreRole(){

    const role = load("selectedRole") || "student";

    Auth.currentRole = role;

    const selected = document.querySelector(

        `.role-option[data-role="${role}"]`

    );

    if(selected){

        selected.classList.add("active");

    }

}

/* ==========================================================
   LOGIN HANDLER
   ========================================================== */

async function loginHandler(event){

    event.preventDefault();

    clearValidation();

    if(!validateLoginForm()){

        showToast(

            "Validation Error",

            "Please correct the highlighted fields.",

            "danger"

        );

        return;

    }

    saveRememberMe();

    await submitLogin();

}

/* ==========================================================
   LOGIN REQUEST
   ========================================================== */

async function submitLogin(){

    setLoading(true);

    try{

        const payload={

            email:elements.email.value.trim(),

            password:elements.password.value,

            role:Auth.currentRole,

            remember:elements.remember
                ?elements.remember.checked
                :false

        };

        const response=await fetch(

            "/login",

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify(payload)

            }

        );

        const data=await response.json();

        if(response.ok && data.success){

            loginSuccess(data);

        }

        else{

            loginFailed(

                data.message ||

                "Invalid credentials."

            );

        }

    }

    catch(error){

        console.error(error);

        loginFailed(

            "Unable to connect to server."

        );

    }

    finally{

        setLoading(false);

    }

}

/* ==========================================================
   LOGIN SUCCESS
   ========================================================== */

function loginSuccess(data){

    showToast(

        "Welcome",

        "Login successful.",

        "success"

    );

    if(data.token){

        save("authToken",data.token);

    }

    if(data.user){

        save("user",data.user);

    }

    setTimeout(()=>{

        redirectUser(data);

    },800);

}

/* ==========================================================
   LOGIN FAILED
   ========================================================== */

function loginFailed(message){

    showToast(

        "Login Failed",

        message,

        "danger"

    );

    shakeLoginForm();

}

/* ==========================================================
   REDIRECT
   ========================================================== */

function redirectUser(data){

    if(data.redirect){

        window.location.href=data.redirect;

        return;

    }

    switch(Auth.currentRole){

        case "admin":

            window.location.href="/admin/dashboard";

            break;

        case "teacher":

            window.location.href="/teacher/dashboard";

            break;

        default:

            window.location.href="/student/dashboard";

    }

}

/* ==========================================================
   SHAKE FORM
   ========================================================== */

function shakeLoginForm(){

    if(!elements.loginForm) return;

    elements.loginForm.classList.add("shake");

    setTimeout(()=>{

        elements.loginForm.classList.remove("shake");

    },500);

}

/* ==========================================================
   CLEAR VALIDATION
   ========================================================== */

function clearValidation(){

    document.querySelectorAll(

        ".is-valid,.is-invalid"

    ).forEach(element=>{

        element.classList.remove(

            "is-valid",

            "is-invalid"

        );

    });

}

/* ==========================================================
   LOGOUT
   ========================================================== */

function logout(){

    remove("authToken");

    remove("user");

    window.location.href="/login";

}

/* ==========================================================
   CHECK LOGIN
   ========================================================== */

function isAuthenticated(){

    return load("authToken") !== null;

}

/* ==========================================================
   AUTH HEADER
   ========================================================== */

function getAuthHeaders(){

    const token = load("authToken");

    return{

        "Authorization":`Bearer ${token}`,

        "Content-Type":"application/json"

    };

}

/* ==========================================================
   SESSION EXPIRED
   ========================================================== */

function sessionExpired(){

    logout();

    showToast(

        "Session Expired",

        "Please login again.",

        "warning"

    );

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        initializeRoleSelection();

    }

);
/* ==========================================================
   PART 4
   REGISTER FORM • PASSWORD CONFIRMATION
   PASSWORD STRENGTH • EMAIL CHECK
   ========================================================== */

/* ==========================================================
   REGISTER ELEMENTS
   ========================================================== */

const register = {

    form: byId("registerForm"),

    username: byId("username"),

    email: byId("registerEmail"),

    password: byId("registerPassword"),

    confirmPassword: byId("confirmPassword"),

    submit: byId("registerBtn"),

    progress: byId("registerProgress")

};

/* ==========================================================
   REGISTER INITIALIZATION
   ========================================================== */

function initializeRegister(){

    if(!register.form) return;

    register.form.addEventListener(

        "submit",

        registerHandler

    );

    if(register.username){

        register.username.addEventListener(

            "input",

            validateUsername

        );

    }

    if(register.email){

        register.email.addEventListener(

            "blur",

            checkEmailAvailability

        );

    }

    if(register.password){

        register.password.addEventListener(

            "input",

            ()=>{

                updatePasswordStrength(

                    register.password.value

                );

                updateRegisterProgress();

            }

        );

    }

    if(register.confirmPassword){

        register.confirmPassword.addEventListener(

            "input",

            validateConfirmPassword

        );

    }

}

/* ==========================================================
   USERNAME VALIDATION
   ========================================================== */

function validateUsername(){

    const value =

        register.username.value.trim();

    if(value.length < 3){

        markInvalid(

            register.username,

            "Minimum 3 characters."

        );

        return false;

    }

    if(!/^[a-zA-Z0-9_]+$/.test(value)){

        markInvalid(

            register.username,

            "Only letters, numbers and _"

        );

        return false;

    }

    markValid(register.username);

    updateRegisterProgress();

    return true;

}

/* ==========================================================
   CONFIRM PASSWORD
   ========================================================== */

function validateConfirmPassword(){

    if(

        register.password.value !==

        register.confirmPassword.value

    ){

        markInvalid(

            register.confirmPassword,

            "Passwords do not match."

        );

        return false;

    }

    markValid(

        register.confirmPassword

    );

    updateRegisterProgress();

    return true;

}

/* ==========================================================
   EMAIL AVAILABILITY
   ========================================================== */

async function checkEmailAvailability(){

    if(

        !validateEmail(

            register.email.value

        )

    ){

        return;

    }

    try{

        const response = await fetch(

            "/check-email",

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify({

                    email:register.email.value

                })

            }

        );

        const data =

            await response.json();

        if(data.available){

            markValid(register.email);

        }

        else{

            markInvalid(

                register.email,

                "Email already exists."

            );

        }

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   REGISTER PROGRESS
   ========================================================== */

function updateRegisterProgress(){

    if(!register.progress) return;

    let score = 0;

    if(

        register.username &&

        validateUsername()

    ){

        score++;

    }

    if(

        register.email &&

        validateEmail(

            register.email.value

        )

    ){

        score++;

    }

    if(

        register.password &&

        validatePassword(

            register.password.value

        )

    ){

        score++;

    }

    if(

        register.confirmPassword &&

        validateConfirmPassword()

    ){

        score++;

    }

    const percent =

        score * 25;

    register.progress.style.width =

        percent + "%";

}

/* ==========================================================
   REGISTER HANDLER
   ========================================================== */

async function registerHandler(event){

    event.preventDefault();

    if(

        !validateUsername() ||

        !validateEmail(

            register.email.value

        ) ||

        !validatePassword(

            register.password.value

        ) ||

        !validateConfirmPassword()

    ){

        showToast(

            "Validation",

            "Please correct the highlighted fields.",

            "danger"

        );

        return;

    }

    registerSubmit();

}

/* ==========================================================
   REGISTER SUBMIT
   ========================================================== */

async function registerSubmit(){

    disable(register.submit);

    register.submit.innerHTML =

        `<span class="spinner"></span>

         Creating Account...`;

    try{

        const response = await fetch(

            "/register",

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify({

                    username:

                        register.username.value,

                    email:

                        register.email.value,

                    password:

                        register.password.value,

                    role:

                        Auth.currentRole

                })

            }

        );

        const data =

            await response.json();

        if(

            response.ok &&

            data.success

        ){

            showToast(

                "Success",

                "Account created successfully.",

                "success"

            );

            register.form.reset();

            if(register.progress){

                register.progress.style.width =

                    "0%";

            }

        }

        else{

            showToast(

                "Registration Failed",

                data.message ||

                "Unable to register.",

                "danger"

            );

        }

    }

    catch(error){

        console.error(error);

        showToast(

            "Network Error",

            "Unable to connect to server.",

            "danger"

        );

    }

    finally{

        enable(register.submit);

        register.submit.innerHTML =

            "Create Account";

    }

}

/* ==========================================================
   INITIALIZE REGISTER
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        initializeRegister();

    }

);
/* ==========================================================
   PART 5
   OTP VERIFICATION • EMAIL VERIFICATION
   RESEND OTP • COUNTDOWN TIMER
   ========================================================== */

/* ==========================================================
   OTP ELEMENTS
   ========================================================== */

const otp = {

    form: byId("otpForm"),

    inputs: document.querySelectorAll(".otp-input"),

    verifyBtn: byId("verifyOtpBtn"),

    resendBtn: byId("resendOtpBtn"),

    timer: byId("otpTimer"),

    email: byId("verificationEmail")

};

/* ==========================================================
   INITIALIZE OTP
   ========================================================== */

function initializeOTP(){

    if(!otp.inputs.length) return;

    otp.inputs.forEach((input,index)=>{

        input.addEventListener(

            "input",

            (event)=>{

                handleOTPInput(event,index);

            }

        );

        input.addEventListener(

            "keydown",

            (event)=>{

                handleOTPKeydown(event,index);

            }

        );

        input.addEventListener(

            "paste",

            pasteOTP

        );

    });

    if(otp.resendBtn){

        otp.resendBtn.addEventListener(

            "click",

            resendOTP

        );

    }

    if(otp.form){

        otp.form.addEventListener(

            "submit",

            verifyOTP

        );

    }

}

/* ==========================================================
   OTP INPUT
   ========================================================== */

function handleOTPInput(event,index){

    const value = event.target.value;

    event.target.value = value.replace(/\D/g,"");

    if(value && index < otp.inputs.length-1){

        otp.inputs[index+1].focus();

    }

    autoSubmitOTP();

}

/* ==========================================================
   BACKSPACE
   ========================================================== */

function handleOTPKeydown(event,index){

    if(

        event.key==="Backspace" &&

        !event.target.value &&

        index>0

    ){

        otp.inputs[index-1].focus();

    }

}

/* ==========================================================
   PASTE OTP
   ========================================================== */

function pasteOTP(event){

    event.preventDefault();

    const pasted =

        event.clipboardData

        .getData("text")

        .replace(/\D/g,"")

        .substring(0,6);

    pasted.split("").forEach((digit,index)=>{

        if(otp.inputs[index]){

            otp.inputs[index].value = digit;

        }

    });

    autoSubmitOTP();

}

/* ==========================================================
   OTP VALUE
   ========================================================== */

function getOTP(){

    let code="";

    otp.inputs.forEach(input=>{

        code+=input.value;

    });

    return code;

}

/* ==========================================================
   AUTO SUBMIT
   ========================================================== */

function autoSubmitOTP(){

    if(getOTP().length===6){

        if(otp.form){

            otp.form.requestSubmit();

        }

    }

}

/* ==========================================================
   VERIFY OTP
   ========================================================== */

async function verifyOTP(event){

    if(event) event.preventDefault();

    const code = getOTP();

    if(code.length!==6){

        showToast(

            "Invalid OTP",

            "Enter a valid 6-digit OTP.",

            "warning"

        );

        return;

    }

    disable(otp.verifyBtn);

    otp.verifyBtn.innerHTML=

        `<span class="spinner"></span> Verifying...`;

    try{

        const response=await fetch(

            "/verify-otp",

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify({

                    otp:code

                })

            }

        );

        const data=await response.json();

        if(response.ok && data.success){

            showToast(

                "Success",

                "OTP Verified Successfully.",

                "success"

            );

            setTimeout(()=>{

                window.location.href=

                    data.redirect ||

                    "/dashboard";

            },800);

        }

        else{

            showToast(

                "Verification Failed",

                data.message ||

                "Invalid OTP.",

                "danger"

            );

            clearOTP();

        }

    }

    catch(error){

        console.error(error);

        showToast(

            "Network Error",

            "Unable to verify OTP.",

            "danger"

        );

    }

    finally{

        enable(otp.verifyBtn);

        otp.verifyBtn.innerHTML=

            "Verify OTP";

    }

}

/* ==========================================================
   RESEND OTP
   ========================================================== */

async function resendOTP(){

    disable(otp.resendBtn);

    try{

        await fetch(

            "/resend-otp",

            {

                method:"POST"

            }

        );

        showToast(

            "OTP Sent",

            "A new OTP has been sent.",

            "success"

        );

        startOTPTimer();

    }

    catch(error){

        showToast(

            "Error",

            "Unable to resend OTP.",

            "danger"

        );

    }

}

/* ==========================================================
   OTP TIMER
   ========================================================== */

function startOTPTimer(){

    clearInterval(Auth.otpTimer);

    Auth.otpSeconds=60;

    updateOTPTimer();

    Auth.otpTimer=setInterval(()=>{

        Auth.otpSeconds--;

        updateOTPTimer();

        if(Auth.otpSeconds<=0){

            clearInterval(Auth.otpTimer);

            enable(otp.resendBtn);

        }

    },1000);

}

function updateOTPTimer(){

    if(!otp.timer) return;

    otp.timer.textContent=

        `${Auth.otpSeconds}s`;

}

/* ==========================================================
   CLEAR OTP
   ========================================================== */

function clearOTP(){

    otp.inputs.forEach(input=>{

        input.value="";

    });

    if(otp.inputs.length){

        otp.inputs[0].focus();

    }

}

/* ==========================================================
   EMAIL VERIFICATION
   ========================================================== */

async function sendVerificationEmail(){

    try{

        const response=await fetch(

            "/send-verification",

            {

                method:"POST"

            }

        );

        const data=await response.json();

        if(data.success){

            showToast(

                "Verification Email",

                "Email sent successfully.",

                "success"

            );

        }

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   OTP INIT
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        initializeOTP();

    }

);
/* ==========================================================
   PART 6
   TWO FACTOR AUTHENTICATION (2FA)
   QR CODE • TRUST DEVICE • SECURITY
   ========================================================== */

/* ==========================================================
   2FA ELEMENTS
   ========================================================== */

const twoFA = {

    form: byId("twoFactorForm"),

    code: byId("twoFactorCode"),

    verifyBtn: byId("verify2FABtn"),

    trustDevice: byId("trustDevice"),

    qrImage: byId("qrImage"),

    secretKey: byId("secretKey"),

    regenerateBtn: byId("regenerateSecret"),

    enableBtn: byId("enable2FA"),

    disableBtn: byId("disable2FA")

};

/* ==========================================================
   INITIALIZE
   ========================================================== */

function initialize2FA(){

    if(twoFA.form){

        twoFA.form.addEventListener(

            "submit",

            verify2FA

        );

    }

    if(twoFA.enableBtn){

        twoFA.enableBtn.addEventListener(

            "click",

            enable2FA

        );

    }

    if(twoFA.disableBtn){

        twoFA.disableBtn.addEventListener(

            "click",

            disable2FA

        );

    }

    if(twoFA.regenerateBtn){

        twoFA.regenerateBtn.addEventListener(

            "click",

            regenerateSecret

        );

    }

}

/* ==========================================================
   ENABLE 2FA
   ========================================================== */

async function enable2FA(){

    try{

        const response = await fetch(

            "/enable-2fa",

            {

                method:"POST",

                headers:getAuthHeaders()

            }

        );

        const data = await response.json();

        if(data.success){

            if(twoFA.secretKey){

                twoFA.secretKey.textContent =

                    data.secret;

            }

            if(twoFA.qrImage){

                twoFA.qrImage.src =

                    data.qr_code;

            }

            showToast(

                "Two-Factor Authentication",

                "Scan the QR code using your Authenticator App.",

                "success"

            );

        }

        else{

            showToast(

                "Error",

                data.message ||

                "Unable to enable 2FA.",

                "danger"

            );

        }

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   VERIFY 2FA
   ========================================================== */

async function verify2FA(event){

    if(event){

        event.preventDefault();

    }

    if(!twoFA.code){

        return;

    }

    const code =

        twoFA.code.value.trim();

    if(code.length !== 6){

        showToast(

            "Invalid Code",

            "Enter a valid 6-digit authenticator code.",

            "warning"

        );

        return;

    }

    disable(twoFA.verifyBtn);

    twoFA.verifyBtn.innerHTML =

        `<span class="spinner"></span> Verifying...`;

    try{

        const response = await fetch(

            "/verify-2fa",

            {

                method:"POST",

                headers:getAuthHeaders(),

                body:JSON.stringify({

                    code:code,

                    trust:

                        twoFA.trustDevice

                        ? twoFA.trustDevice.checked

                        : false

                })

            }

        );

        const data =

            await response.json();

        if(response.ok && data.success){

            showToast(

                "Verified",

                "Two-factor authentication successful.",

                "success"

            );

            if(data.redirect){

                window.location.href =

                    data.redirect;

            }

        }

        else{

            showToast(

                "Verification Failed",

                data.message ||

                "Invalid authentication code.",

                "danger"

            );

            twoFA.code.focus();

        }

    }

    catch(error){

        console.error(error);

        showToast(

            "Network Error",

            "Unable to verify authentication code.",

            "danger"

        );

    }

    finally{

        enable(twoFA.verifyBtn);

        twoFA.verifyBtn.innerHTML =

            "Verify";

    }

}

/* ==========================================================
   DISABLE 2FA
   ========================================================== */

async function disable2FA(){

    const confirmDisable = confirm(

        "Disable Two-Factor Authentication?"

    );

    if(!confirmDisable){

        return;

    }

    try{

        const response = await fetch(

            "/disable-2fa",

            {

                method:"POST",

                headers:getAuthHeaders()

            }

        );

        const data =

            await response.json();

        if(data.success){

            showToast(

                "Disabled",

                "Two-factor authentication has been disabled.",

                "success"

            );

        }

        else{

            showToast(

                "Error",

                data.message ||

                "Unable to disable 2FA.",

                "danger"

            );

        }

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   REGENERATE SECRET
   ========================================================== */

async function regenerateSecret(){

    try{

        const response = await fetch(

            "/regenerate-2fa-secret",

            {

                method:"POST",

                headers:getAuthHeaders()

            }

        );

        const data =

            await response.json();

        if(data.success){

            if(twoFA.secretKey){

                twoFA.secretKey.textContent =

                    data.secret;

            }

            if(twoFA.qrImage){

                twoFA.qrImage.src =

                    data.qr_code;

            }

            showToast(

                "New Secret Generated",

                "Update your authenticator application.",

                "info"

            );

        }

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   TRUSTED DEVICE
   ========================================================== */

function rememberTrustedDevice(){

    if(

        twoFA.trustDevice &&

        twoFA.trustDevice.checked

    ){

        save(

            "trustedDevice",

            true

        );

    }

}

function isTrustedDevice(){

    return load(

        "trustedDevice"

    ) === true;

}

/* ==========================================================
   SECURITY CHECK
   ========================================================== */

function securityCheck(){

    const token =

        load("authToken");

    if(!token){

        return false;

    }

    if(token.length < 20){

        console.warn(

            "Suspicious authentication token."

        );

    }

    return true;

}

/* ==========================================================
   AUTO LOGOUT
   ========================================================== */

let inactivityTimer;

function resetInactivityTimer(){

    clearTimeout(inactivityTimer);

    inactivityTimer = setTimeout(

        ()=>{

            showToast(

                "Session Timeout",

                "You have been logged out due to inactivity.",

                "warning"

            );

            logout();

        },

        30 * 60 * 1000

    );

}

["mousemove","keydown","click","scroll"]

.forEach(eventName=>{

    document.addEventListener(

        eventName,

        resetInactivityTimer

    );

});

/* ==========================================================
   INITIALIZE 2FA
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        initialize2FA();

        resetInactivityTimer();

    }

);
/* ==========================================================
   PART 7
   THEME • LANGUAGE • LOCAL STORAGE
   SESSION MANAGEMENT • USER PROFILE
   ========================================================== */

/* ==========================================================
   USER PREFERENCES
   ========================================================== */

const Preferences = {

    theme: load("theme") || "light",

    language: load("language") || "en",

    remember: load("rememberMe") || false

};

/* ==========================================================
   THEME
   ========================================================== */

function initializeTheme(){

    if(Preferences.theme === "dark"){

        document.body.classList.add("dark-mode");

    }

    updateThemeButton();

}

function updateThemeButton(){

    const icon = byId("themeIcon");

    if(!icon) return;

    if(document.body.classList.contains("dark-mode")){

        icon.classList.remove("fa-moon");
        icon.classList.add("fa-sun");

    }else{

        icon.classList.remove("fa-sun");
        icon.classList.add("fa-moon");

    }

}

function switchTheme(){

    document.body.classList.toggle("dark-mode");

    Preferences.theme =
        document.body.classList.contains("dark-mode")
            ? "dark"
            : "light";

    save("theme", Preferences.theme);

    updateThemeButton();

}

/* ==========================================================
   LANGUAGE
   ========================================================== */

function initializeLanguage(){

    const selector = byId("language");

    if(!selector) return;

    selector.value = Preferences.language;

    selector.addEventListener(

        "change",

        changeLanguage

    );

}

function changeLanguage(event){

    Preferences.language = event.target.value;

    save(

        "language",

        Preferences.language

    );

    showToast(

        "Language Updated",

        "Reload the page to apply language changes.",

        "info"

    );

}

/* ==========================================================
   USER PROFILE
   ========================================================== */

async function loadCurrentUser(){

    if(!isAuthenticated()){

        return;

    }

    try{

        const response = await fetch(

            "/api/me",

            {

                headers:getAuthHeaders()

            }

        );

        if(!response.ok){

            return;

        }

        const user = await response.json();

        save(

            "currentUser",

            user

        );

        updateProfileUI(user);

    }

    catch(error){

        console.error(error);

    }

}

function updateProfileUI(user){

    const name = byId("profileName");

    const email = byId("profileEmail");

    const avatar = byId("profileAvatar");

    if(name){

        name.textContent =

            user.name || "";

    }

    if(email){

        email.textContent =

            user.email || "";

    }

    if(avatar && user.avatar){

        avatar.src = user.avatar;

    }

}

/* ==========================================================
   SESSION
   ========================================================== */

function initializeSession(){

    if(!isAuthenticated()){

        return;

    }

    const expiry = load("sessionExpiry");

    if(!expiry){

        return;

    }

    if(Date.now() > expiry){

        sessionExpired();

    }

}

function refreshSession(){

    const expires =

        Date.now() +

        (60 * 60 * 1000);

    save(

        "sessionExpiry",

        expires

    );

}

function clearSession(){

    remove("authToken");

    remove("currentUser");

    remove("sessionExpiry");

}

/* ==========================================================
   AUTO REFRESH SESSION
   ========================================================== */

setInterval(()=>{

    if(isAuthenticated()){

        refreshSession();

    }

},300000);

/* ==========================================================
   PROFILE MENU
   ========================================================== */

function toggleProfileMenu(){

    const menu =

        byId("profileMenu");

    if(menu){

        menu.classList.toggle("show");

    }

}

document.addEventListener(

    "click",

    (event)=>{

        const menu =

            byId("profileMenu");

        const button =

            byId("profileButton");

        if(

            menu &&

            button &&

            !menu.contains(event.target) &&

            !button.contains(event.target)

        ){

            menu.classList.remove("show");

        }

    }

);

/* ==========================================================
   LAST LOGIN
   ========================================================== */

function saveLastLogin(){

    save(

        "lastLogin",

        new Date().toISOString()

    );

}

function showLastLogin(){

    const last = load("lastLogin");

    const element = byId("lastLogin");

    if(last && element){

        element.textContent =

            new Date(last).toLocaleString();

    }

}

/* ==========================================================
   ONLINE / OFFLINE
   ========================================================== */

window.addEventListener(

    "online",

    ()=>{

        showToast(

            "Online",

            "Internet connection restored.",

            "success"

        );

    }

);

window.addEventListener(

    "offline",

    ()=>{

        showToast(

            "Offline",

            "You are currently offline.",

            "warning"

        );

    }

);

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        initializeTheme();

        initializeLanguage();

        initializeSession();

        loadCurrentUser();

        showLastLogin();

    }

);
/* ==========================================================
   PART 8
   FORGOT PASSWORD • RESET PASSWORD
   CAPTCHA • FORM SWITCHING
   ========================================================== */

/* ==========================================================
   FORGOT PASSWORD
   ========================================================== */

const forgotPassword = {

    form: byId("forgotPasswordForm"),

    email: byId("forgotEmail"),

    submit: byId("forgotSubmit")

};

function initializeForgotPassword(){

    if(!forgotPassword.form) return;

    forgotPassword.form.addEventListener(

        "submit",

        forgotPasswordHandler

    );

}

async function forgotPasswordHandler(event){

    event.preventDefault();

    const email = forgotPassword.email.value.trim();

    if(!validateEmail(email)){

        showToast(

            "Invalid Email",

            "Please enter a valid email address.",

            "warning"

        );

        return;

    }

    disable(forgotPassword.submit);

    forgotPassword.submit.innerHTML =

        `<span class="spinner"></span> Sending...`;

    try{

        const response = await fetch(

            "/forgot-password",

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify({

                    email:email

                })

            }

        );

        const data = await response.json();

        if(response.ok && data.success){

            showToast(

                "Email Sent",

                "Password reset instructions have been sent to your email.",

                "success"

            );

        }else{

            showToast(

                "Failed",

                data.message ||

                "Unable to process request.",

                "danger"

            );

        }

    }catch(error){

        console.error(error);

        showToast(

            "Network Error",

            "Unable to connect to server.",

            "danger"

        );

    }

    finally{

        enable(forgotPassword.submit);

        forgotPassword.submit.innerHTML =

            "Send Reset Link";

    }

}

/* ==========================================================
   RESET PASSWORD
   ========================================================== */

const resetPassword = {

    form: byId("resetPasswordForm"),

    password: byId("newPassword"),

    confirm: byId("confirmNewPassword"),

    submit: byId("resetPasswordBtn")

};

function initializeResetPassword(){

    if(!resetPassword.form) return;

    resetPassword.form.addEventListener(

        "submit",

        resetPasswordHandler

    );

}

async function resetPasswordHandler(event){

    event.preventDefault();

    if(

        resetPassword.password.value !==

        resetPassword.confirm.value

    ){

        showToast(

            "Password Mismatch",

            "Passwords do not match.",

            "danger"

        );

        return;

    }

    if(

        !validatePassword(

            resetPassword.password.value

        )

    ){

        showToast(

            "Weak Password",

            "Password must be at least 8 characters.",

            "warning"

        );

        return;

    }

    disable(resetPassword.submit);

    resetPassword.submit.innerHTML =

        `<span class="spinner"></span> Resetting...`;

    try{

        const token = byId("resetToken")?.value || "";

        const response = await fetch(

            "/reset-password",

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify({

                    token:token,

                    password:resetPassword.password.value

                })

            }

        );

        const data = await response.json();

        if(response.ok && data.success){

            showToast(

                "Password Updated",

                "You can now login using your new password.",

                "success"

            );

            setTimeout(()=>{

                window.location.href="/login";

            },1200);

        }else{

            showToast(

                "Reset Failed",

                data.message ||

                "Unable to reset password.",

                "danger"

            );

        }

    }catch(error){

        console.error(error);

    }

    finally{

        enable(resetPassword.submit);

        resetPassword.submit.innerHTML =

            "Reset Password";

    }

}

/* ==========================================================
   CAPTCHA
   ========================================================== */

function generateCaptcha(){

    const text =

        Math.random()

        .toString(36)

        .substring(2,8)

        .toUpperCase();

    save(

        "captcha",

        text

    );

    const box = byId("captchaText");

    if(box){

        box.textContent = text;

    }

}

function validateCaptcha(){

    const input =

        byId("captchaInput");

    if(!input) return true;

    return (

        input.value.trim().toUpperCase() ===

        load("captcha")

    );

}

function refreshCaptcha(){

    generateCaptcha();

}

/* ==========================================================
   FORM SWITCHING
   ========================================================== */

function showLoginForm(){

    show(

        byId("loginSection")

    );

    hide(

        byId("registerSection")

    );

    hide(

        byId("forgotSection")

    );

}

function showRegisterForm(){

    hide(

        byId("loginSection")

    );

    show(

        byId("registerSection")

    );

    hide(

        byId("forgotSection")

    );

}

function showForgotPasswordForm(){

    hide(

        byId("loginSection")

    );

    hide(

        byId("registerSection")

    );

    show(

        byId("forgotSection")

    );

}

/* ==========================================================
   BIND LINKS
   ========================================================== */

function bindNavigationLinks(){

    byId("showLogin")?.addEventListener(

        "click",

        showLoginForm

    );

    byId("showRegister")?.addEventListener(

        "click",

        showRegisterForm

    );

    byId("showForgot")?.addEventListener(

        "click",

        showForgotPasswordForm

    );

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        initializeForgotPassword();

        initializeResetPassword();

        generateCaptcha();

        bindNavigationLinks();

    }

);
/* ==========================================================
   PART 9
   ANIMATIONS • ACCESSIBILITY • KEYBOARD SHORTCUTS
   MOBILE SUPPORT • PERFORMANCE
   ========================================================== */

/* ==========================================================
   PAGE ANIMATIONS
   ========================================================== */

function fadeIn(element){

    if(!element) return;

    element.classList.remove("fade-in");

    void element.offsetWidth;

    element.classList.add("fade-in");

}

function shake(element){

    if(!element) return;

    element.classList.remove("shake");

    void element.offsetWidth;

    element.classList.add("shake");

}

function highlight(element){

    if(!element) return;

    element.classList.add("border-primary");

    setTimeout(()=>{

        element.classList.remove("border-primary");

    },1200);

}

/* ==========================================================
   ACCESSIBILITY
   ========================================================== */

function focusFirstInput(){

    const input=document.querySelector(

        "input:not([type='hidden'])"

    );

    if(input){

        input.focus();

    }

}

function enableKeyboardNavigation(){

    document.addEventListener("keydown",(event)=>{

        if(event.key==="Escape"){

            document.querySelectorAll(".modal.show")

            .forEach(modal=>{

                modal.classList.remove("show");

            });

        }

    });

}

/* ==========================================================
   KEYBOARD SHORTCUTS
   ========================================================== */

document.addEventListener("keydown",(event)=>{

    if(event.ctrlKey && event.key==="l"){

        event.preventDefault();

        byId("email")?.focus();

    }

    if(event.ctrlKey && event.key==="k"){

        event.preventDefault();

        byId("password")?.focus();

    }

    if(event.key==="Enter"){

        const active=document.activeElement;

        if(

            active &&

            active.classList.contains("otp-input")

        ){

            autoSubmitOTP();

        }

    }

});

/* ==========================================================
   MOBILE MENU
   ========================================================== */

function toggleMobileMenu(){

    const menu=byId("mobileMenu");

    if(menu){

        menu.classList.toggle("show");

    }

}

/* ==========================================================
   INPUT AUTO TRIM
   ========================================================== */

function trimInputs(){

    document.querySelectorAll("input").forEach(input=>{

        input.addEventListener("blur",()=>{

            input.value=input.value.trim();

        });

    });

}

/* ==========================================================
   DISABLE DOUBLE SUBMIT
   ========================================================== */

function preventDoubleSubmit(form){

    if(!form) return;

    form.addEventListener("submit",()=>{

        const button=form.querySelector(

            "button[type='submit']"

        );

        if(button){

            button.disabled=true;

            setTimeout(()=>{

                button.disabled=false;

            },3000);

        }

    });

}

/* ==========================================================
   COPY TO CLIPBOARD
   ========================================================== */

async function copyText(text){

    try{

        await navigator.clipboard.writeText(text);

        showToast(

            "Copied",

            "Copied to clipboard.",

            "success"

        );

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   NETWORK STATUS
   ========================================================== */

function monitorConnection(){

    window.addEventListener("online",()=>{

        showToast(

            "Connected",

            "Internet connection restored.",

            "success"

        );

    });

    window.addEventListener("offline",()=>{

        showToast(

            "Offline",

            "Internet connection lost.",

            "warning"

        );

    });

}

/* ==========================================================
   PERFORMANCE
   ========================================================== */

function debounce(callback,delay=300){

    let timer;

    return (...args)=>{

        clearTimeout(timer);

        timer=setTimeout(()=>{

            callback(...args);

        },delay);

    };

}

function throttle(callback,limit=200){

    let waiting=false;

    return (...args)=>{

        if(waiting) return;

        callback(...args);

        waiting=true;

        setTimeout(()=>{

            waiting=false;

        },limit);

    };

}

/* ==========================================================
   AUTO SAVE FORM
   ========================================================== */

function autoSaveLogin(){

    if(elements.email){

        save(

            "draftEmail",

            elements.email.value

        );

    }

}

function restoreDraft(){

    const email=load("draftEmail");

    if(email && elements.email){

        elements.email.value=email;

    }

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener("DOMContentLoaded",()=>{

    focusFirstInput();

    enableKeyboardNavigation();

    trimInputs();

    monitorConnection();

    restoreDraft();

    if(elements.loginForm){

        preventDoubleSubmit(

            elements.loginForm

        );

    }

    window.addEventListener(

        "beforeunload",

        autoSaveLogin

    );

});
/* ==========================================================
   PART 10
   BOOTSTRAP • UTILITIES • PERFORMANCE
   GLOBAL ERROR HANDLING • FINAL INITIALIZATION
   ========================================================== */

"use strict";

/* ==========================================================
   BOOTSTRAP INITIALIZATION
   ========================================================== */

function initializeBootstrap(){

    if(typeof bootstrap === "undefined"){

        return;

    }

    document.querySelectorAll('[data-bs-toggle="tooltip"]')

    .forEach(element=>{

        new bootstrap.Tooltip(element);

    });

    document.querySelectorAll('[data-bs-toggle="popover"]')

    .forEach(element=>{

        new bootstrap.Popover(element);

    });

}

/* ==========================================================
   MODAL HELPERS
   ========================================================== */

function openModal(id){

    const modal = document.getElementById(id);

    if(!modal || typeof bootstrap === "undefined") return;

    const instance = new bootstrap.Modal(modal);

    instance.show();

}

function closeModal(id){

    const modal = document.getElementById(id);

    if(!modal || typeof bootstrap === "undefined") return;

    const instance = bootstrap.Modal.getInstance(modal);

    if(instance){

        instance.hide();

    }

}

/* ==========================================================
   SCROLL HELPERS
   ========================================================== */

function scrollTopSmooth(){

    window.scrollTo({

        top:0,

        behavior:"smooth"

    });

}

function scrollToElement(id){

    const element = document.getElementById(id);

    if(element){

        element.scrollIntoView({

            behavior:"smooth",

            block:"center"

        });

    }

}

/* ==========================================================
   GLOBAL FETCH WRAPPER
   ========================================================== */

async function apiRequest(url, options = {}){

    const config = {

        headers:{

            "Content-Type":"application/json",

            ...getAuthHeaders(),

            ...(options.headers || {})

        },

        ...options

    };

    const response = await fetch(url, config);

    if(response.status === 401){

        sessionExpired();

        throw new Error("Unauthorized");

    }

    return response;

}

/* ==========================================================
   ERROR HANDLING
   ========================================================== */

window.addEventListener("error",(event)=>{

    console.error("Application Error:", event.error);

});

window.addEventListener("unhandledrejection",(event)=>{

    console.error("Unhandled Promise:", event.reason);

});

/* ==========================================================
   CONNECTION CHECK
   ========================================================== */

function checkConnection(){

    if(!navigator.onLine){

        showToast(

            "Offline",

            "Some features may not work without internet.",

            "warning"

        );

    }

}

/* ==========================================================
   PAGE VISIBILITY
   ========================================================== */

document.addEventListener(

    "visibilitychange",

    ()=>{

        if(document.visibilityState === "visible"){

            refreshSession();

        }

    }

);

/* ==========================================================
   STORAGE CLEANUP
   ========================================================== */

function cleanupStorage(){

    const keys = [

        "draftEmail",

        "captcha"

    ];

    keys.forEach(remove);

}

/* ==========================================================
   LOGGING
   ========================================================== */

function log(message){

    console.log(

        `[AUTH] ${message}`

    );

}

/* ==========================================================
   VERSION
   ========================================================== */

const AUTH_VERSION = "1.0.0";

function printVersion(){

    console.log(

        `%cLab Auto Grader Authentication v${AUTH_VERSION}`,

        "color:#2563eb;font-size:14px;font-weight:bold;"

    );

}

/* ==========================================================
   FINAL INITIALIZATION
   ========================================================== */

function initializeAuth(){

    initializeBootstrap();

    checkConnection();

    cleanupStorage();

    printVersion();

    log("Authentication initialized.");

}

document.addEventListener(

    "DOMContentLoaded",

    initializeAuth

);

/* ==========================================================
   GLOBAL EXPORTS (OPTIONAL)
   ========================================================== */

window.AuthApp = {

    login: loginHandler,

    logout: logout,

    toggleTheme: switchTheme,

    showToast: showToast,

    openModal: openModal,

    closeModal: closeModal,

    apiRequest: apiRequest,

    scrollTop: scrollTopSmooth

};

/* ==========================================================
   END OF AUTH.JS
   ========================================================== */