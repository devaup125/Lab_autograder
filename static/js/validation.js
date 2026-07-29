/* ==========================================================
   LAB AUTO GRADER
   Validation JavaScript
   Part 1
   ========================================================== */

"use strict";

/* ==========================================================
   VALIDATION OBJECT
   ========================================================== */

const Validation = {

    forms: [],

    errors: {},

    valid: true,

    debounceTimer: null

};

/* ==========================================================
   DOM READY
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        initializeValidation();

    }

);

/* ==========================================================
   INITIALIZATION
   ========================================================== */

function initializeValidation(){

    bindValidationForms();

    bindRequiredFields();

}

/* ==========================================================
   FORM BINDING
   ========================================================== */

function bindValidationForms(){

    document.querySelectorAll("form")

    .forEach(form=>{

        form.setAttribute(

            "novalidate",

            "true"

        );

    });

}

/* ==========================================================
   REQUIRED FIELDS
   ========================================================== */

function bindRequiredFields(){

    document.querySelectorAll(

        "[required]"

    )

    .forEach(field=>{

        field.addEventListener(

            "blur",

            ()=>{

                validateRequired(field);

            }

        );

    });

}

/* ==========================================================
   REQUIRED VALIDATION
   ========================================================== */

function validateRequired(field){

    if(

        field.value.trim()===""

    ){

        showFieldError(

            field,

            "This field is required."

        );

        return false;

    }

    clearFieldError(field);

    return true;

}

/* ==========================================================
   ERROR DISPLAY
   ========================================================== */

function showFieldError(

    field,

    message

){

    field.classList.remove(

        "is-valid"

    );

    field.classList.add(

        "is-invalid"

    );

    let feedback =

        field.parentElement.querySelector(

            ".invalid-feedback"

        );

    if(!feedback){

        feedback =

            document.createElement("div");

        feedback.className =

            "invalid-feedback";

        field.parentElement.appendChild(

            feedback

        );

    }

    feedback.textContent = message;

}

/* ==========================================================
   SUCCESS DISPLAY
   ========================================================== */

function showFieldSuccess(field){

    field.classList.remove(

        "is-invalid"

    );

    field.classList.add(

        "is-valid"

    );

}

/* ==========================================================
   CLEAR ERROR
   ========================================================== */

function clearFieldError(field){

    field.classList.remove(

        "is-invalid"

    );

    field.classList.add(

        "is-valid"

    );

}

/* ==========================================================
   RESET FORM
   ========================================================== */

function resetValidation(form){

    form.querySelectorAll(

        ".is-valid,.is-invalid"

    )

    .forEach(field=>{

        field.classList.remove(

            "is-valid",

            "is-invalid"

        );

    });

}

/* ==========================================================
   VALIDATION SUMMARY
   ========================================================== */

function showValidationSummary(

    messages

){

    const box =

        document.getElementById(

            "validationSummary"

        );

    if(!box) return;

    box.innerHTML =

        messages

        .map(msg=>`<li>${msg}</li>`)

        .join("");

}

/* ==========================================================
   UTILITIES
   ========================================================== */

function byId(id){

    return document.getElementById(id);

}

function trim(value){

    return value.trim();

}

function isEmpty(value){

    return trim(value)==="";

}

function debounce(callback,delay=300){

    clearTimeout(

        Validation.debounceTimer

    );

    Validation.debounceTimer =

        setTimeout(

            callback,

            delay

        );

}

/* ==========================================================
   PLACEHOLDERS
   ========================================================== */

function validateForm(){}

function validateInput(){}

function validateField(){}
/* ==========================================================
   PART 2
   EMAIL • USERNAME • PASSWORD • PHONE • URL VALIDATION
   ========================================================== */

"use strict";

/* ==========================================================
   EMAIL VALIDATION
   ========================================================== */

function validateEmail(email){

    const regex =

        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return regex.test(

        trim(email)

    );

}

function validateEmailField(field){

    if(!validateEmail(field.value)){

        showFieldError(

            field,

            "Please enter a valid email address."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   USERNAME VALIDATION
   ========================================================== */

function validateUsername(username){

    const regex =

        /^[a-zA-Z0-9_]{3,20}$/;

    return regex.test(

        trim(username)

    );

}

function validateUsernameField(field){

    if(!validateUsername(field.value)){

        showFieldError(

            field,

            "Username must be 3-20 characters (letters, numbers or _)."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   PASSWORD VALIDATION
   ========================================================== */

function validatePassword(password){

    return (

        password.length >= 8 &&

        /[A-Z]/.test(password) &&

        /[a-z]/.test(password) &&

        /[0-9]/.test(password)

    );

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

function updatePasswordStrength(field){

    const meter =

        byId("passwordStrength");

    if(!meter) return;

    const score =

        passwordStrength(field.value);

    meter.value = score;

}

function validatePasswordField(field){

    if(!validatePassword(field.value)){

        showFieldError(

            field,

            "Password must contain uppercase, lowercase, number and at least 8 characters."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   CONFIRM PASSWORD
   ========================================================== */

function validateConfirmPassword(

    passwordField,

    confirmField

){

    if(

        passwordField.value !==

        confirmField.value

    ){

        showFieldError(

            confirmField,

            "Passwords do not match."

        );

        return false;

    }

    showFieldSuccess(

        confirmField

    );

    return true;

}

/* ==========================================================
   PHONE VALIDATION
   ========================================================== */

function validatePhone(phone){

    const regex =

        /^[6-9]\d{9}$/;

    return regex.test(

        trim(phone)

    );

}

function validatePhoneField(field){

    if(!validatePhone(field.value)){

        showFieldError(

            field,

            "Enter a valid 10-digit mobile number."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   URL VALIDATION
   ========================================================== */

function validateURL(url){

    try{

        new URL(url);

        return true;

    }

    catch{

        return false;

    }

}

function validateURLField(field){

    if(

        field.value.trim()!=="" &&

        !validateURL(field.value)

    ){

        showFieldError(

            field,

            "Invalid URL."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   LIVE VALIDATION
   ========================================================== */

function bindLiveValidation(){

    document.querySelectorAll(

        "input[type='email']"

    ).forEach(field=>{

        field.addEventListener(

            "input",

            ()=>{

                validateEmailField(field);

            }

        );

    });

    document.querySelectorAll(

        ".username"

    ).forEach(field=>{

        field.addEventListener(

            "input",

            ()=>{

                validateUsernameField(field);

            }

        );

    });

    document.querySelectorAll(

        ".phone"

    ).forEach(field=>{

        field.addEventListener(

            "input",

            ()=>{

                validatePhoneField(field);

            }

        );

    });

}

/* ==========================================================
   PASSWORD EVENTS
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        const password =

            byId("password");

        if(password){

            password.addEventListener(

                "input",

                ()=>{

                    updatePasswordStrength(

                        password

                    );

                    validatePasswordField(

                        password

                    );

                }

            );

        }

        const confirm =

            byId("confirmPassword");

        if(password && confirm){

            confirm.addEventListener(

                "input",

                ()=>{

                    validateConfirmPassword(

                        password,

                        confirm

                    );

                }

            );

        }

        bindLiveValidation();

    }

);
/* ==========================================================
   PART 3
   STUDENT • TEACHER • ADMIN • PROFILE VALIDATION
   ========================================================== */

"use strict";

/* ==========================================================
   STUDENT VALIDATION
   ========================================================== */

function validateStudentForm(form){

    let valid = true;

    const requiredFields = [

        "studentName",

        "studentEmail",

        "studentRoll",

        "studentDepartment",

        "studentSemester"

    ];

    requiredFields.forEach(id=>{

        const field = byId(id);

        if(field && !validateRequired(field)){

            valid = false;

        }

    });

    const email = byId("studentEmail");

    if(email && !validateEmailField(email)){

        valid = false;

    }

    const roll = byId("studentRoll");

    if(roll && !validateRollNumber(roll)){

        valid = false;

    }

    return valid;

}

/* ==========================================================
   TEACHER VALIDATION
   ========================================================== */

function validateTeacherForm(form){

    let valid = true;

    const requiredFields = [

        "teacherName",

        "teacherEmail",

        "teacherDepartment",

        "teacherEmployeeId"

    ];

    requiredFields.forEach(id=>{

        const field = byId(id);

        if(field && !validateRequired(field)){

            valid = false;

        }

    });

    const email = byId("teacherEmail");

    if(email && !validateEmailField(email)){

        valid = false;

    }

    return valid;

}

/* ==========================================================
   ADMIN VALIDATION
   ========================================================== */

function validateAdminForm(form){

    let valid = true;

    const name = byId("adminName");

    const email = byId("adminEmail");

    const phone = byId("adminPhone");

    if(name && !validateRequired(name)){

        valid = false;

    }

    if(email && !validateEmailField(email)){

        valid = false;

    }

    if(phone && !validatePhoneField(phone)){

        valid = false;

    }

    return valid;

}

/* ==========================================================
   PROFILE VALIDATION
   ========================================================== */

function validateProfileForm(form){

    let valid = true;

    const fields = form.querySelectorAll(

        "[required]"

    );

    fields.forEach(field=>{

        if(!validateRequired(field)){

            valid = false;

        }

    });

    return valid;

}

/* ==========================================================
   ROLL NUMBER
   ========================================================== */

function validateRollNumber(field){

    const regex = /^[0-9]{10,15}$/;

    if(!regex.test(field.value.trim())){

        showFieldError(

            field,

            "Invalid roll number."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   EMPLOYEE ID
   ========================================================== */

function validateEmployeeId(field){

    const regex =

        /^[A-Za-z0-9-]{4,20}$/;

    if(!regex.test(field.value.trim())){

        showFieldError(

            field,

            "Invalid Employee ID."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   DEPARTMENT
   ========================================================== */

function validateDepartment(field){

    if(field.value===""){

        showFieldError(

            field,

            "Please select a department."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   SEMESTER
   ========================================================== */

function validateSemester(field){

    const value = parseInt(field.value);

    if(isNaN(value) || value < 1 || value > 8){

        showFieldError(

            field,

            "Semester must be between 1 and 8."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   SECTION
   ========================================================== */

function validateSection(field){

    const regex = /^[A-Z]$/;

    if(

        field.value.trim()!=="" &&

        !regex.test(field.value.trim())

    ){

        showFieldError(

            field,

            "Section must be A-Z."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   PROFILE IMAGE
   ========================================================== */

function validateProfileImage(field){

    if(field.files.length===0){

        return true;

    }

    const file = field.files[0];

    const allowed = [

        "image/jpeg",

        "image/png",

        "image/webp"

    ];

    if(!allowed.includes(file.type)){

        showFieldError(

            field,

            "Only JPG, PNG and WEBP images are allowed."

        );

        return false;

    }

    if(file.size > 2*1024*1024){

        showFieldError(

            field,

            "Image size must be below 2 MB."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   EVENTS
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        byId("studentRoll")

        ?.addEventListener(

            "blur",

            function(){

                validateRollNumber(this);

            }

        );

        byId("teacherEmployeeId")

        ?.addEventListener(

            "blur",

            function(){

                validateEmployeeId(this);

            }

        );

        byId("studentSemester")

        ?.addEventListener(

            "change",

            function(){

                validateSemester(this);

            }

        );

        byId("studentDepartment")

        ?.addEventListener(

            "change",

            function(){

                validateDepartment(this);

            }

        );

        byId("profileImage")

        ?.addEventListener(

            "change",

            function(){

                validateProfileImage(this);

            }

        );

    }

);
/* ==========================================================
   PART 4
   ASSIGNMENT • PROBLEM • TEST CASE • MARKS VALIDATION
   ========================================================== */

"use strict";

/* ==========================================================
   ASSIGNMENT FORM
   ========================================================== */

function validateAssignmentForm(form){

    let valid = true;

    const title = byId("assignmentTitle");
    const description = byId("assignmentDescription");
    const dueDate = byId("assignmentDueDate");
    const totalMarks = byId("assignmentMarks");

    if(title && !validateRequired(title)) valid = false;
    if(description && !validateRequired(description)) valid = false;
    if(dueDate && !validateDueDate(dueDate)) valid = false;
    if(totalMarks && !validateMarks(totalMarks)) valid = false;

    return valid;

}

/* ==========================================================
   PROBLEM FORM
   ========================================================== */

function validateProblemForm(form){

    let valid = true;

    const fields = [

        "problemTitle",
        "problemStatement",
        "problemDifficulty",
        "problemLanguage"

    ];

    fields.forEach(id=>{

        const field = byId(id);

        if(field && !validateRequired(field)){

            valid = false;

        }

    });

    const timeLimit = byId("timeLimit");

    if(timeLimit && !validateTimeLimit(timeLimit)){

        valid = false;

    }

    const memoryLimit = byId("memoryLimit");

    if(memoryLimit && !validateMemoryLimit(memoryLimit)){

        valid = false;

    }

    return valid;

}

/* ==========================================================
   TEST CASE VALIDATION
   ========================================================== */

function validateTestCaseForm(){

    let valid = true;

    const input = byId("testInput");
    const output = byId("testOutput");

    if(input && !validateRequired(input)){

        valid = false;

    }

    if(output && !validateRequired(output)){

        valid = false;

    }

    return valid;

}

/* ==========================================================
   MARKS
   ========================================================== */

function validateMarks(field){

    const value = Number(field.value);

    if(

        isNaN(value) ||

        value < 0 ||

        value > 100

    ){

        showFieldError(

            field,

            "Marks must be between 0 and 100."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   DUE DATE
   ========================================================== */

function validateDueDate(field){

    const selected = new Date(field.value);

    const today = new Date();

    today.setHours(0,0,0,0);

    if(selected <= today){

        showFieldError(

            field,

            "Due date must be in the future."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   TIME LIMIT
   ========================================================== */

function validateTimeLimit(field){

    const value = Number(field.value);

    if(

        isNaN(value) ||

        value <= 0 ||

        value > 30

    ){

        showFieldError(

            field,

            "Time limit must be between 1 and 30 seconds."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   MEMORY LIMIT
   ========================================================== */

function validateMemoryLimit(field){

    const value = Number(field.value);

    if(

        isNaN(value) ||

        value < 16 ||

        value > 2048

    ){

        showFieldError(

            field,

            "Memory limit must be between 16 MB and 2048 MB."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   DIFFICULTY
   ========================================================== */

function validateDifficulty(field){

    const allowed = [

        "Easy",

        "Medium",

        "Hard"

    ];

    if(!allowed.includes(field.value)){

        showFieldError(

            field,

            "Select a valid difficulty."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   LANGUAGE
   ========================================================== */

function validateLanguage(field){

    const allowed = [

        "Python",

        "C",

        "C++",

        "Java",

        "JavaScript"

    ];

    if(!allowed.includes(field.value)){

        showFieldError(

            field,

            "Unsupported language."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   SAMPLE TEST CASE COUNT
   ========================================================== */

function validateTestCaseCount(field){

    const count = Number(field.value);

    if(

        isNaN(count) ||

        count < 1 ||

        count > 50

    ){

        showFieldError(

            field,

            "Test case count must be between 1 and 50."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   EVENTS
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        byId("assignmentDueDate")

        ?.addEventListener(

            "change",

            function(){

                validateDueDate(this);

            }

        );

        byId("assignmentMarks")

        ?.addEventListener(

            "input",

            function(){

                validateMarks(this);

            }

        );

        byId("timeLimit")

        ?.addEventListener(

            "input",

            function(){

                validateTimeLimit(this);

            }

        );

        byId("memoryLimit")

        ?.addEventListener(

            "input",

            function(){

                validateMemoryLimit(this);

            }

        );

        byId("problemDifficulty")

        ?.addEventListener(

            "change",

            function(){

                validateDifficulty(this);

            }

        );

        byId("problemLanguage")

        ?.addEventListener(

            "change",

            function(){

                validateLanguage(this);

            }

        );

        byId("testCaseCount")

        ?.addEventListener(

            "input",

            function(){

                validateTestCaseCount(this);

            }

        );

    }

);
/* ==========================================================
   PART 5
   COURSE • BATCH • DEPARTMENT • SEMESTER
   SECTION • ACADEMIC YEAR VALIDATION
   ========================================================== */

"use strict";

/* ==========================================================
   COURSE VALIDATION
   ========================================================== */

function validateCourseForm(form){

    let valid = true;

    const courseCode = byId("courseCode");
    const courseName = byId("courseName");
    const department = byId("courseDepartment");
    const semester = byId("courseSemester");
    const credits = byId("courseCredits");

    if(courseCode && !validateCourseCode(courseCode))
        valid = false;

    if(courseName && !validateRequired(courseName))
        valid = false;

    if(department && !validateDepartment(department))
        valid = false;

    if(semester && !validateSemester(semester))
        valid = false;

    if(credits && !validateCredits(credits))
        valid = false;

    return valid;

}

/* ==========================================================
   COURSE CODE
   ========================================================== */

function validateCourseCode(field){

    const regex = /^[A-Z]{2,6}[0-9]{3,5}$/;

    if(!regex.test(field.value.trim())){

        showFieldError(
            field,
            "Invalid course code (e.g. CS101)."
        );

        return false;
    }

    showFieldSuccess(field);
    return true;

}

/* ==========================================================
   CREDITS
   ========================================================== */

function validateCredits(field){

    const value = Number(field.value);

    if(

        isNaN(value) ||

        value < 1 ||

        value > 10

    ){

        showFieldError(
            field,
            "Credits must be between 1 and 10."
        );

        return false;
    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   BATCH VALIDATION
   ========================================================== */

function validateBatch(field){

    const regex = /^[0-9]{4}-[0-9]{4}$/;

    if(!regex.test(field.value.trim())){

        showFieldError(
            field,
            "Batch format must be YYYY-YYYY."
        );

        return false;
    }

    const years = field.value.split("-");

    if(Number(years[1]) !== Number(years[0]) + 4){

        showFieldError(
            field,
            "Engineering batch should span 4 years."
        );

        return false;
    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   ACADEMIC YEAR
   ========================================================== */

function validateAcademicYear(field){

    const regex = /^[0-9]{4}-[0-9]{2}$/;

    if(!regex.test(field.value.trim())){

        showFieldError(
            field,
            "Format should be YYYY-YY."
        );

        return false;
    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   SECTION
   ========================================================== */

function validateSectionField(field){

    const allowed = [

        "A","B","C","D","E","F"

    ];

    if(

        !allowed.includes(

            field.value.toUpperCase()

        )

    ){

        showFieldError(
            field,
            "Section must be between A and F."
        );

        return false;
    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   CLASS STRENGTH
   ========================================================== */

function validateClassStrength(field){

    const strength = Number(field.value);

    if(

        isNaN(strength) ||

        strength < 1 ||

        strength > 300

    ){

        showFieldError(
            field,
            "Class strength must be between 1 and 300."
        );

        return false;
    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   PROGRAM
   ========================================================== */

function validateProgram(field){

    const allowed = [

        "B.Tech",

        "M.Tech",

        "MCA",

        "BCA",

        "B.Sc",

        "M.Sc"

    ];

    if(

        !allowed.includes(field.value)

    ){

        showFieldError(
            field,
            "Please select a valid program."
        );

        return false;
    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   COURSE NAME LENGTH
   ========================================================== */

function validateCourseName(field){

    if(

        field.value.trim().length < 3 ||

        field.value.trim().length > 100

    ){

        showFieldError(
            field,
            "Course name should contain 3-100 characters."
        );

        return false;
    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   EVENTS
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        byId("courseCode")
        ?.addEventListener(
            "blur",
            function(){
                validateCourseCode(this);
            }
        );

        byId("courseCredits")
        ?.addEventListener(
            "input",
            function(){
                validateCredits(this);
            }
        );

        byId("batch")
        ?.addEventListener(
            "blur",
            function(){
                validateBatch(this);
            }
        );

        byId("academicYear")
        ?.addEventListener(
            "blur",
            function(){
                validateAcademicYear(this);
            }
        );

        byId("section")
        ?.addEventListener(
            "change",
            function(){
                validateSectionField(this);
            }
        );

        byId("classStrength")
        ?.addEventListener(
            "input",
            function(){
                validateClassStrength(this);
            }
        );

        byId("program")
        ?.addEventListener(
            "change",
            function(){
                validateProgram(this);
            }
        );

        byId("courseName")
        ?.addEventListener(
            "blur",
            function(){
                validateCourseName(this);
            }
        );

    }

);
/* ==========================================================
   PART 6
   FILE UPLOAD • IMAGE • PDF • ZIP
   SOURCE CODE VALIDATION
   ========================================================== */

"use strict";

/* ==========================================================
   FILE CONFIGURATION
   ========================================================== */

const FileValidation = {

    maxImageSize: 2 * 1024 * 1024,      // 2 MB

    maxPdfSize: 10 * 1024 * 1024,       // 10 MB

    maxZipSize: 50 * 1024 * 1024,       // 50 MB

    maxCodeSize: 2 * 1024 * 1024        // 2 MB

};

/* ==========================================================
   GENERIC FILE VALIDATION
   ========================================================== */

function validateFile(field, allowedTypes, maxSize){

    if(!field.files || field.files.length === 0){

        return true;

    }

    const file = field.files[0];

    if(!allowedTypes.includes(file.type)){

        showFieldError(

            field,

            "Unsupported file type."

        );

        return false;

    }

    if(file.size > maxSize){

        showFieldError(

            field,

            `Maximum allowed size is ${Math.round(maxSize/1024/1024)} MB.`

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   IMAGE
   ========================================================== */

function validateImage(field){

    return validateFile(

        field,

        [

            "image/jpeg",

            "image/png",

            "image/webp",

            "image/gif"

        ],

        FileValidation.maxImageSize

    );

}

/* ==========================================================
   PDF
   ========================================================== */

function validatePDF(field){

    return validateFile(

        field,

        [

            "application/pdf"

        ],

        FileValidation.maxPdfSize

    );

}

/* ==========================================================
   ZIP
   ========================================================== */

function validateZIP(field){

    return validateFile(

        field,

        [

            "application/zip",

            "application/x-zip-compressed"

        ],

        FileValidation.maxZipSize

    );

}

/* ==========================================================
   SOURCE CODE
   ========================================================== */

function validateSourceCode(field){

    if(!field.files || field.files.length===0){

        return true;

    }

    const file = field.files[0];

    const allowedExtensions = [

        ".py",

        ".c",

        ".cpp",

        ".java",

        ".js"

    ];

    const name = file.name.toLowerCase();

    const valid = allowedExtensions.some(

        ext => name.endsWith(ext)

    );

    if(!valid){

        showFieldError(

            field,

            "Only .py, .c, .cpp, .java and .js files are allowed."

        );

        return false;

    }

    if(file.size > FileValidation.maxCodeSize){

        showFieldError(

            field,

            "Source code file must be smaller than 2 MB."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   FILE NAME
   ========================================================== */

function validateFileName(field){

    if(!field.files || field.files.length===0){

        return true;

    }

    const file = field.files[0];

    const regex = /^[A-Za-z0-9_. -]+$/;

    if(!regex.test(file.name)){

        showFieldError(

            field,

            "Filename contains invalid characters."

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   MULTIPLE FILES
   ========================================================== */

function validateFileCount(field, maxFiles = 5){

    if(field.files.length > maxFiles){

        showFieldError(

            field,

            `Maximum ${maxFiles} files allowed.`

        );

        return false;

    }

    showFieldSuccess(field);

    return true;

}

/* ==========================================================
   FILE PREVIEW
   ========================================================== */

function previewImage(field, previewId){

    if(!field.files.length){

        return;

    }

    const preview = byId(previewId);

    if(!preview){

        return;

    }

    const reader = new FileReader();

    reader.onload = function(e){

        preview.src = e.target.result;

    };

    reader.readAsDataURL(field.files[0]);

}

/* ==========================================================
   EVENTS
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        byId("profileImage")

        ?.addEventListener(

            "change",

            function(){

                validateImage(this);

                previewImage(

                    this,

                    "profilePreview"

                );

            }

        );

        byId("assignmentPDF")

        ?.addEventListener(

            "change",

            function(){

                validatePDF(this);

            }

        );

        byId("problemZIP")

        ?.addEventListener(

            "change",

            function(){

                validateZIP(this);

            }

        );

        byId("sourceCode")

        ?.addEventListener(

            "change",

            function(){

                validateSourceCode(this);

                validateFileName(this);

            }

        );

        byId("multipleFiles")

        ?.addEventListener(

            "change",

            function(){

                validateFileCount(this);

            }

        );

    }

);
/* ==========================================================
   PART 7
   REAL-TIME VALIDATION • INPUT FORMATTING
   CHARACTER COUNTER • AUTO FORMATTING
   ========================================================== */

"use strict";

/* ==========================================================
   CHARACTER COUNTER
   ========================================================== */

function updateCharacterCounter(field, counterId, maxLength){

    const counter = byId(counterId);

    if(!counter) return;

    const length = field.value.length;

    counter.textContent = `${length}/${maxLength}`;

    if(length > maxLength){

        counter.classList.add("text-danger");

        showFieldError(field, `Maximum ${maxLength} characters allowed.`);

    }else{

        counter.classList.remove("text-danger");

        clearFieldError(field);

    }

}

/* ==========================================================
   AUTO CAPITALIZE WORDS
   ========================================================== */

function autoCapitalize(field){

    field.value = field.value.replace(

        /\b\w/g,

        char => char.toUpperCase()

    );

}

/* ==========================================================
   REMOVE EXTRA SPACES
   ========================================================== */

function removeExtraSpaces(field){

    field.value = field.value.replace(/\s+/g," ").trim();

}

/* ==========================================================
   PHONE FORMAT
   ========================================================== */

function formatPhone(field){

    field.value = field.value.replace(/\D/g,"");

    if(field.value.length > 10){

        field.value = field.value.substring(0,10);

    }

}

/* ==========================================================
   ROLL NUMBER FORMAT
   ========================================================== */

function formatRollNumber(field){

    field.value = field.value.replace(/[^0-9]/g,"");

}

/* ==========================================================
   USERNAME FORMAT
   ========================================================== */

function formatUsername(field){

    field.value = field.value

        .toLowerCase()

        .replace(/\s+/g,"")

        .replace(/[^a-z0-9_]/g,"");

}

/* ==========================================================
   COURSE CODE FORMAT
   ========================================================== */

function formatCourseCode(field){

    field.value = field.value

        .toUpperCase()

        .replace(/\s+/g,"");

}

/* ==========================================================
   NUMERIC ONLY
   ========================================================== */

function numericOnly(field){

    field.value = field.value.replace(/[^0-9]/g,"");

}

/* ==========================================================
   DECIMAL FORMAT
   ========================================================== */

function decimalOnly(field){

    field.value = field.value.replace(/[^0-9.]/g,"");

}

/* ==========================================================
   LIVE VALIDATION
   ========================================================== */

function bindRealtimeValidation(){

    document.querySelectorAll("[data-validate]")

    .forEach(field=>{

        field.addEventListener(

            "input",

            ()=>{

                const type = field.dataset.validate;

                switch(type){

                    case "email":

                        validateEmailField(field);

                        break;

                    case "username":

                        formatUsername(field);

                        validateUsernameField(field);

                        break;

                    case "phone":

                        formatPhone(field);

                        validatePhoneField(field);

                        break;

                    case "roll":

                        formatRollNumber(field);

                        validateRollNumber(field);

                        break;

                    case "course":

                        formatCourseCode(field);

                        validateCourseCode(field);

                        break;

                }

            }

        );

    });

}

/* ==========================================================
   TEXTAREA LIMIT
   ========================================================== */

function bindCharacterCounters(){

    document.querySelectorAll("[maxlength]")

    .forEach(field=>{

        const counterId =

            field.dataset.counter;

        if(!counterId) return;

        field.addEventListener(

            "input",

            ()=>{

                updateCharacterCounter(

                    field,

                    counterId,

                    Number(field.maxLength)

                );

            }

        );

    });

}

/* ==========================================================
   AUTO FORMAT TEXT FIELDS
   ========================================================== */

function bindAutoFormatting(){

    document.querySelectorAll(".auto-capitalize")

    .forEach(field=>{

        field.addEventListener(

            "blur",

            ()=>{

                autoCapitalize(field);

            }

        );

    });

    document.querySelectorAll(".trim-input")

    .forEach(field=>{

        field.addEventListener(

            "blur",

            ()=>{

                removeExtraSpaces(field);

            }

        );

    });

}

/* ==========================================================
   COPY PASTE SANITIZATION
   ========================================================== */

function sanitizePaste(event){

    event.preventDefault();

    const text =

        (event.clipboardData ||

        window.clipboardData)

        .getData("text");

    const cleaned =

        text.replace(/\s+/g," ");

    document.execCommand(

        "insertText",

        false,

        cleaned

    );

}

/* ==========================================================
   EVENTS
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        bindRealtimeValidation();

        bindCharacterCounters();

        bindAutoFormatting();

        document.querySelectorAll("input,textarea")

        .forEach(field=>{

            field.addEventListener(

                "paste",

                sanitizePaste

            );

        });

    }

);
/* ==========================================================
   PART 8
   FORM SUBMISSION • AJAX VALIDATION
   SERVER ERRORS • LOADING • DUPLICATE SUBMISSION
   ========================================================== */

"use strict";

/* ==========================================================
   FORM SUBMISSION STATE
   ========================================================== */

const FormSubmission = {

    isSubmitting: false

};

/* ==========================================================
   LOADING
   ========================================================== */

function showFormLoading(form){

    const button = form.querySelector(

        "button[type='submit']"

    );

    if(!button) return;

    button.disabled = true;

    button.dataset.originalText =

        button.innerHTML;

    button.innerHTML =

        `<span class="spinner-border spinner-border-sm me-2"></span>
         Please wait...`;

}

function hideFormLoading(form){

    const button = form.querySelector(

        "button[type='submit']"

    );

    if(!button) return;

    button.disabled = false;

    button.innerHTML =

        button.dataset.originalText ||

        "Submit";

}

/* ==========================================================
   SERVER ERROR
   ========================================================== */

function showServerErrors(errors){

    if(!errors) return;

    Object.keys(errors).forEach(key=>{

        const field = byId(key);

        if(field){

            showFieldError(

                field,

                errors[key]

            );

        }

    });

}

/* ==========================================================
   CLEAR SERVER ERRORS
   ========================================================== */

function clearServerErrors(form){

    form.querySelectorAll(

        ".is-invalid"

    ).forEach(field=>{

        clearFieldError(field);

    });

}

/* ==========================================================
   AJAX SUBMIT
   ========================================================== */

async function submitFormAjax(form){

    if(FormSubmission.isSubmitting){

        return;

    }

    FormSubmission.isSubmitting = true;

    clearServerErrors(form);

    showFormLoading(form);

    try{

        const formData =

            new FormData(form);

        const response = await fetch(

            form.action,

            {

                method:form.method || "POST",

                body:formData

            }

        );

        const result =

            await response.json();

        if(result.success){

            handleFormSuccess(

                result,

                form

            );

        }

        else{

            showServerErrors(

                result.errors

            );

            if(result.message){

                alert(

                    result.message

                );

            }

        }

    }

    catch(error){

        console.error(error);

        alert(

            "Unable to connect to server."

        );

    }

    finally{

        hideFormLoading(form);

        FormSubmission.isSubmitting = false;

    }

}

/* ==========================================================
   SUCCESS
   ========================================================== */

function handleFormSuccess(

    result,

    form

){

    if(result.redirect){

        window.location.href =

            result.redirect;

        return;

    }

    if(result.message){

        alert(result.message);

    }

    if(form.dataset.reset==="true"){

        form.reset();

        resetValidation(form);

    }

}

/* ==========================================================
   VALIDATE BEFORE SUBMIT
   ========================================================== */

function validateBeforeSubmit(form){

    let valid = true;

    form.querySelectorAll("[required]")

    .forEach(field=>{

        if(!validateRequired(field)){

            valid = false;

        }

    });

    return valid;

}

/* ==========================================================
   PREVENT DUPLICATE SUBMISSION
   ========================================================== */

function preventDuplicateSubmit(form){

    form.addEventListener(

        "submit",

        event=>{

            if(FormSubmission.isSubmitting){

                event.preventDefault();

            }

        }

    );

}

/* ==========================================================
   AJAX FORM
   ========================================================== */

function bindAjaxForms(){

    document.querySelectorAll(

        "form[data-ajax='true']"

    )

    .forEach(form=>{

        preventDuplicateSubmit(form);

        form.addEventListener(

            "submit",

            async event=>{

                event.preventDefault();

                if(

                    validateBeforeSubmit(form)

                ){

                    await submitFormAjax(

                        form

                    );

                }

            }

        );

    });

}

/* ==========================================================
   FORM RESET
   ========================================================== */

function bindResetButtons(){

    document.querySelectorAll(

        "button[type='reset']"

    )

    .forEach(button=>{

        button.addEventListener(

            "click",

            ()=>{

                const form =

                    button.closest("form");

                if(form){

                    resetValidation(form);

                }

            }

        );

    });

}

/* ==========================================================
   AUTO SAVE DRAFT
   ========================================================== */

function autoSaveDraft(form){

    const data = {};

    new FormData(form).forEach((value,key)=>{

        data[key] = value;

    });

    localStorage.setItem(

        form.id+"_draft",

        JSON.stringify(data)

    );

}

function restoreDraft(form){

    const draft =

        localStorage.getItem(

            form.id+"_draft"

        );

    if(!draft) return;

    try{

        const values =

            JSON.parse(draft);

        Object.keys(values).forEach(key=>{

            if(form.elements[key]){

                form.elements[key].value =

                    values[key];

            }

        });

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        bindAjaxForms();

        bindResetButtons();

        document.querySelectorAll("form")

        .forEach(form=>{

            restoreDraft(form);

            form.addEventListener(

                "input",

                ()=>{

                    debounce(()=>{

                        autoSaveDraft(form);

                    },500);

                }

            );

        });

    }

);
/* ==========================================================
   PART 9
   ACCESSIBILITY • KEYBOARD NAVIGATION • TOOLTIPS
   AUTO FOCUS • PERFORMANCE OPTIMIZATION
   ========================================================== */

"use strict";

/* ==========================================================
   ACCESSIBILITY
   ========================================================== */

function applyAccessibility() {

    document.querySelectorAll("input, textarea, select").forEach(field => {

        if (!field.hasAttribute("aria-label")) {

            const label = document.querySelector(`label[for="${field.id}"]`);

            if (label) {
                field.setAttribute("aria-label", label.textContent.trim());
            }

        }

        if (!field.hasAttribute("autocomplete")) {
            field.setAttribute("autocomplete", "off");
        }

    });

}

/* ==========================================================
   AUTO FOCUS FIRST ERROR
   ========================================================== */

function focusFirstError() {

    const firstError = document.querySelector(".is-invalid");

    if (firstError) {

        firstError.focus({
            preventScroll: false
        });

        firstError.scrollIntoView({

            behavior: "smooth",

            block: "center"

        });

    }

}

/* ==========================================================
   KEYBOARD NAVIGATION
   ========================================================== */

function initializeKeyboardNavigation() {

    document.addEventListener("keydown", function(event) {

        if (event.key === "Enter") {

            const active = document.activeElement;

            if (

                active.tagName === "INPUT" ||

                active.tagName === "SELECT"

            ) {

                const form = active.form;

                if (!form) return;

                const fields = Array.from(

                    form.querySelectorAll(

                        "input, select, textarea, button"

                    )

                ).filter(el =>

                    !el.disabled &&

                    el.type !== "hidden"

                );

                const index = fields.indexOf(active);

                if (

                    index >= 0 &&

                    index < fields.length - 1

                ) {

                    event.preventDefault();

                    fields[index + 1].focus();

                }

            }

        }

    });

}

/* ==========================================================
   BOOTSTRAP TOOLTIPS
   ========================================================== */

function initializeValidationTooltips() {

    if (typeof bootstrap === "undefined") return;

    document.querySelectorAll("[data-bs-toggle='tooltip']").forEach(el => {

        new bootstrap.Tooltip(el);

    });

}

/* ==========================================================
   HELP TEXT
   ========================================================== */

function showHelp(field, message) {

    let help = field.parentElement.querySelector(".form-text");

    if (!help) {

        help = document.createElement("small");

        help.className = "form-text text-muted";

        field.parentElement.appendChild(help);

    }

    help.textContent = message;

}

/* ==========================================================
   CLEAR HELP
   ========================================================== */

function clearHelp(field) {

    const help = field.parentElement.querySelector(".form-text");

    if (help) {

        help.remove();

    }

}

/* ==========================================================
   PASSWORD CAPS LOCK
   ========================================================== */

function detectCapsLock(field) {

    field.addEventListener("keyup", function(event) {

        const warning = byId("capsLockWarning");

        if (!warning) return;

        if (event.getModifierState("CapsLock")) {

            warning.classList.remove("d-none");

        } else {

            warning.classList.add("d-none");

        }

    });

}

/* ==========================================================
   SCROLL TO FIRST ERROR
   ========================================================== */

function scrollToFirstError() {

    const error = document.querySelector(".is-invalid");

    if (error) {

        error.scrollIntoView({

            behavior: "smooth",

            block: "center"

        });

    }

}

/* ==========================================================
   PERFORMANCE
   ========================================================== */

function optimizeValidationPerformance() {

    const observer = new MutationObserver(() => {

        document.querySelectorAll(".invalid-feedback").forEach(msg => {

            if (msg.textContent.trim() === "") {

                msg.remove();

            }

        });

    });

    observer.observe(document.body, {

        childList: true,

        subtree: true

    });

}

/* ==========================================================
   FORM PROGRESS
   ========================================================== */

function updateFormProgress(formId, progressId) {

    const form = byId(formId);

    const progress = byId(progressId);

    if (!form || !progress) return;

    const fields = form.querySelectorAll("[required]");

    let completed = 0;

    fields.forEach(field => {

        if (field.value.trim() !== "") {

            completed++;

        }

    });

    const percent = Math.round(

        (completed / fields.length) * 100

    );

    progress.style.width = percent + "%";

    progress.textContent = percent + "%";

}

/* ==========================================================
   AUTO UPDATE PROGRESS
   ========================================================== */

function bindFormProgress() {

    document.querySelectorAll("form[data-progress]").forEach(form => {

        const progressId = form.dataset.progress;

        form.addEventListener("input", () => {

            updateFormProgress(

                form.id,

                progressId

            );

        });

    });

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    () => {

        applyAccessibility();

        initializeKeyboardNavigation();

        initializeValidationTooltips();

        optimizeValidationPerformance();

        bindFormProgress();

        const password = byId("password");

        if (password) {

            detectCapsLock(password);

        }

    }

);
/* ==========================================================
   PART 10
   BOOTSTRAP • GLOBAL API • ERROR HANDLING
   FINAL INITIALIZATION
   ========================================================== */

"use strict";

/* ==========================================================
   VERSION
   ========================================================== */

const VALIDATION_VERSION = "1.0.0";

/* ==========================================================
   BOOTSTRAP INITIALIZATION
   ========================================================== */

function initializeBootstrapValidation(){

    if(typeof bootstrap === "undefined"){

        return;

    }

    document

        .querySelectorAll('[data-bs-toggle="tooltip"]')

        .forEach(element=>{

            new bootstrap.Tooltip(element);

        });

}

/* ==========================================================
   GLOBAL VALIDATE
   ========================================================== */

function validateEntireForm(form){

    let valid = true;

    const requiredFields = form.querySelectorAll("[required]");

    requiredFields.forEach(field=>{

        if(!validateRequired(field)){

            valid = false;

        }

    });

    if(!valid){

        focusFirstError();

    }

    return valid;

}

/* ==========================================================
   RESET UTILITIES
   ========================================================== */

function resetForm(form){

    if(!form) return;

    form.reset();

    resetValidation(form);

}

function clearValidationSummary(){

    const summary = byId("validationSummary");

    if(summary){

        summary.innerHTML = "";

    }

}

/* ==========================================================
   GLOBAL ERROR HANDLING
   ========================================================== */

window.addEventListener("error", event=>{

    console.error(

        "Validation Error:",

        event.error

    );

});

window.addEventListener(

    "unhandledrejection",

    event=>{

        console.error(

            "Promise Error:",

            event.reason

        );

    }

);

/* ==========================================================
   AUTO BIND ALL FORMS
   ========================================================== */

function bindAllForms(){

    document.querySelectorAll("form")

    .forEach(form=>{

        form.addEventListener(

            "submit",

            event=>{

                if(!validateEntireForm(form)){

                    event.preventDefault();

                }

            }

        );

    });

}

/* ==========================================================
   CLEAR DRAFTS
   ========================================================== */

function clearAllDrafts(){

    document.querySelectorAll("form")

    .forEach(form=>{

        localStorage.removeItem(

            form.id + "_draft"

        );

    });

}

/* ==========================================================
   VERSION
   ========================================================== */

function printValidationVersion(){

    console.log(

        `%cLab Auto Grader Validation v${VALIDATION_VERSION}`,

        "color:#198754;font-size:14px;font-weight:bold;"

    );

}

/* ==========================================================
   FINAL INITIALIZATION
   ========================================================== */

function initializeValidationApplication(){

    initializeBootstrapValidation();

    bindAllForms();

    printValidationVersion();

    console.log(

        "Validation system initialized."

    );

}

/* ==========================================================
   DOM READY
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        initializeValidationApplication();

    }

);

/* ==========================================================
   GLOBAL EXPORTS
   ========================================================== */

window.ValidationApp = {

    validateEntireForm,

    validateEmail,

    validateUsername,

    validatePassword,

    validatePhone,

    validateURL,

    validateStudentForm,

    validateTeacherForm,

    validateAdminForm,

    validateAssignmentForm,

    validateProblemForm,

    validateCourseForm,

    validateFile,

    validateImage,

    validatePDF,

    validateZIP,

    validateSourceCode,

    resetForm,

    clearAllDrafts,

    showFieldError,

    showFieldSuccess,

    clearFieldError

};

/* ==========================================================
   END OF VALIDATION.JS
   ========================================================== */