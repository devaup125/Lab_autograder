/* ==========================================================
   LAB AUTO GRADER
   Monaco Editor Integration
   Part 1
   ========================================================== */

"use strict";

/* ==========================================================
   MONACO CONFIGURATION
   ========================================================== */

const MonacoApp = {

    editor: null,

    currentLanguage: "python",

    currentTheme: "vs-dark",

    autoSave: true,

    fontSize: 16,

    tabSize: 4,

    readOnly: false,

    storageKey: "lab_autograder_code"

};

/* ==========================================================
   LANGUAGE MAP
   ========================================================== */

const LanguageMap = {

    python: "python",

    c: "c",

    cpp: "cpp",

    java: "java",

    javascript: "javascript"

};

/* ==========================================================
   DOM READY
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        initializeMonaco();

    }

);

/* ==========================================================
   LOAD MONACO
   ========================================================== */

function initializeMonaco(){

    if(typeof require === "undefined"){

        console.error(

            "Monaco Loader not found."

        );

        return;

    }

    require.config({

        paths:{

            vs:

            "/static/monaco/min/vs"

        }

    });

    require(

        ["vs/editor/editor.main"],

        ()=>{

            createEditor();

        }

    );

}

/* ==========================================================
   CREATE EDITOR
   ========================================================== */

function createEditor(){

    const container =

        document.getElementById(

            "monacoEditor"

        );

    if(!container){

        console.warn(

            "Editor container missing."

        );

        return;

    }

    MonacoApp.editor = monaco.editor.create(

        container,

        {

            value:getDefaultTemplate(

                MonacoApp.currentLanguage

            ),

            language:

                MonacoApp.currentLanguage,

            theme:

                MonacoApp.currentTheme,

            automaticLayout:true,

            fontSize:

                MonacoApp.fontSize,

            tabSize:

                MonacoApp.tabSize,

            minimap:{

                enabled:true

            },

            scrollBeyondLastLine:false,

            roundedSelection:true,

            wordWrap:"on",

            smoothScrolling:true,

            cursorBlinking:"smooth",

            renderWhitespace:"selection",

            formatOnPaste:true,

            formatOnType:true,

            readOnly:

                MonacoApp.readOnly

        }

    );

    registerEvents();

    restoreCode();

}

/* ==========================================================
   EVENTS
   ========================================================== */

function registerEvents(){

    if(!MonacoApp.editor) return;

    MonacoApp.editor.onDidChangeModelContent(

        ()=>{

            if(

                MonacoApp.autoSave

            ){

                saveCode();

            }

        }

    );

}

/* ==========================================================
   DEFAULT CODE
   ========================================================== */

function getDefaultTemplate(language){

    switch(language){

        case "python":

            return `print("Hello, World!")`;

        case "java":

            return `public class Main {

    public static void main(String[] args){

        System.out.println("Hello World");

    }

}`;

        case "c":

            return `#include <stdio.h>

int main(){

    printf("Hello World");

    return 0;

}`;

        case "cpp":

            return `#include <iostream>

using namespace std;

int main(){

    cout<<"Hello World";

    return 0;

}`;

        default:

            return "";

    }

}

/* ==========================================================
   SAVE CODE
   ========================================================== */

function saveCode(){

    if(!MonacoApp.editor) return;

    localStorage.setItem(

        MonacoApp.storageKey,

        MonacoApp.editor.getValue()

    );

}

/* ==========================================================
   RESTORE CODE
   ========================================================== */

function restoreCode(){

    if(!MonacoApp.editor) return;

    const code =

        localStorage.getItem(

            MonacoApp.storageKey

        );

    if(code){

        MonacoApp.editor.setValue(

            code

        );

    }

}

/* ==========================================================
   UTILITIES
   ========================================================== */

function getEditor(){

    return MonacoApp.editor;

}

function getCode(){

    if(!MonacoApp.editor){

        return "";

    }

    return MonacoApp.editor.getValue();

}

function setCode(code){

    if(MonacoApp.editor){

        MonacoApp.editor.setValue(

            code

        );

    }

}

function clearEditor(){

    setCode("");

}
/* ==========================================================
   PART 2
   LANGUAGE SWITCHING • BOILERPLATES
   FONT SIZE • THEME • EDITOR OPTIONS
   ========================================================== */

"use strict";

/* ==========================================================
   LANGUAGE TEMPLATES
   ========================================================== */

const CodeTemplates = {

    python: `def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
`,

    c: `#include <stdio.h>

int main() {

    printf("Hello, World!\\n");

    return 0;
}
`,

    cpp: `#include <iostream>

using namespace std;

int main() {

    cout << "Hello, World!" << endl;

    return 0;
}
`,

    java: `public class Main {

    public static void main(String[] args) {

        System.out.println("Hello, World!");

    }

}
`,

    javascript: `function main(){

    console.log("Hello, World!");

}

main();
`

};

/* ==========================================================
   LANGUAGE SWITCHING
   ========================================================== */

function changeLanguage(language){

    if(!MonacoApp.editor) return;

    if(!LanguageMap[language]){

        console.warn("Unsupported language:", language);

        return;

    }

    MonacoApp.currentLanguage = language;

    const model = MonacoApp.editor.getModel();

    monaco.editor.setModelLanguage(

        model,

        LanguageMap[language]

    );

    localStorage.setItem(

        "selected_language",

        language

    );

}

/* ==========================================================
   LOAD TEMPLATE
   ========================================================== */

function loadTemplate(language){

    if(!MonacoApp.editor) return;

    if(confirm("Replace current code with the default template?")){

        MonacoApp.editor.setValue(

            CodeTemplates[language] ||

            ""

        );

    }

}

/* ==========================================================
   RESTORE LANGUAGE
   ========================================================== */

function restoreLanguage(){

    const language =

        localStorage.getItem(

            "selected_language"

        );

    if(language){

        changeLanguage(language);

        const selector =

            document.getElementById(

                "languageSelect"

            );

        if(selector){

            selector.value = language;

        }

    }

}

/* ==========================================================
   FONT SIZE
   ========================================================== */

function increaseFontSize(){

    MonacoApp.fontSize++;

    updateEditorOptions();

}

function decreaseFontSize(){

    if(MonacoApp.fontSize > 10){

        MonacoApp.fontSize--;

        updateEditorOptions();

    }

}

function setFontSize(size){

    MonacoApp.fontSize = size;

    updateEditorOptions();

}

/* ==========================================================
   THEME
   ========================================================== */

function changeTheme(theme){

    MonacoApp.currentTheme = theme;

    monaco.editor.setTheme(theme);

    localStorage.setItem(

        "editor_theme",

        theme

    );

}

function restoreEditorTheme(){

    const theme =

        localStorage.getItem(

            "editor_theme"

        );

    if(theme){

        changeTheme(theme);

    }

}

/* ==========================================================
   EDITOR OPTIONS
   ========================================================== */

function updateEditorOptions(){

    if(!MonacoApp.editor) return;

    MonacoApp.editor.updateOptions({

        fontSize: MonacoApp.fontSize,

        tabSize: MonacoApp.tabSize,

        minimap:{

            enabled:true

        },

        wordWrap:"on",

        automaticLayout:true

    });

}

/* ==========================================================
   TAB SIZE
   ========================================================== */

function setTabSize(size){

    MonacoApp.tabSize = size;

    updateEditorOptions();

}

/* ==========================================================
   READ ONLY
   ========================================================== */

function setReadOnly(value){

    MonacoApp.readOnly = value;

    MonacoApp.editor.updateOptions({

        readOnly:value

    });

}

/* ==========================================================
   AUTO SAVE
   ========================================================== */

function enableAutoSave(){

    MonacoApp.autoSave = true;

}

function disableAutoSave(){

    MonacoApp.autoSave = false;

}

/* ==========================================================
   RESET EDITOR
   ========================================================== */

function resetEditor(){

    loadTemplate(

        MonacoApp.currentLanguage

    );

}

/* ==========================================================
   BIND UI
   ========================================================== */

function bindEditorControls(){

    document.getElementById("languageSelect")

    ?.addEventListener(

        "change",

        function(){

            changeLanguage(this.value);

        }

    );

    document.getElementById("themeSelect")

    ?.addEventListener(

        "change",

        function(){

            changeTheme(this.value);

        }

    );

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        bindEditorControls();

        restoreLanguage();

        restoreEditorTheme();

    }

);
/* ==========================================================
   PART 3
   RUN CODE • SUBMIT CODE • API INTEGRATION
   OUTPUT PANEL • LOADING
   ========================================================== */

"use strict";

/* ==========================================================
   API ENDPOINTS
   ========================================================== */

const MonacoAPI = {

    run: "/api/code/run",

    submit: "/api/code/submit",

    save: "/api/code/save"

};

/* ==========================================================
   RUN CODE
   ========================================================== */

async function runCode(){

    if(!MonacoApp.editor){

        return;

    }

    showEditorLoading();

    clearOutput();

    try{

        const response = await fetch(

            MonacoAPI.run,

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify({

                    language:MonacoApp.currentLanguage,

                    code:getCode(),

                    input:getCustomInput()

                })

            }

        );

        const result = await response.json();

        displayExecutionResult(result);

    }

    catch(error){

        console.error(error);

        displayError(

            "Unable to execute code."

        );

    }

    finally{

        hideEditorLoading();

    }

}

/* ==========================================================
   SUBMIT CODE
   ========================================================== */

async function submitCode(){

    if(!MonacoApp.editor){

        return;

    }

    if(!confirm(

        "Submit this solution?"

    )){

        return;

    }

    showEditorLoading();

    try{

        const response = await fetch(

            MonacoAPI.submit,

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify({

                    language:MonacoApp.currentLanguage,

                    code:getCode(),

                    problem_id:getProblemId()

                })

            }

        );

        const result = await response.json();

        showSubmissionResult(result);

    }

    catch(error){

        console.error(error);

        displayError(

            "Submission failed."

        );

    }

    finally{

        hideEditorLoading();

    }

}

/* ==========================================================
   SAVE DRAFT
   ========================================================== */

async function saveDraft(){

    try{

        await fetch(

            MonacoAPI.save,

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify({

                    language:MonacoApp.currentLanguage,

                    code:getCode()

                })

            }

        );

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   OUTPUT PANEL
   ========================================================== */

function getOutputPanel(){

    return document.getElementById(

        "outputPanel"

    );

}

function clearOutput(){

    const panel = getOutputPanel();

    if(panel){

        panel.textContent = "";

    }

}

function appendOutput(text){

    const panel = getOutputPanel();

    if(panel){

        panel.textContent += text + "\n";

    }

}

/* ==========================================================
   EXECUTION RESULT
   ========================================================== */

function displayExecutionResult(result){

    clearOutput();

    if(result.error){

        displayError(result.error);

        return;

    }

    appendOutput(

        "===== OUTPUT ====="

    );

    appendOutput(

        result.output || ""

    );

    appendOutput("");

    appendOutput(

        `Execution Time : ${result.execution_time || "0"} ms`

    );

    appendOutput(

        `Memory Used    : ${result.memory || "0"} KB`

    );

}

/* ==========================================================
   SUBMISSION RESULT
   ========================================================== */

function showSubmissionResult(result){

    if(result.success){

        appendOutput(

            "Submission Successful"

        );

        appendOutput(

            `Score : ${result.score}`

        );

        appendOutput(

            `Passed : ${result.passed}`

        );

        appendOutput(

            `Failed : ${result.failed}`

        );

    }

    else{

        displayError(

            result.message ||

            "Submission Failed"

        );

    }

}

/* ==========================================================
   ERROR DISPLAY
   ========================================================== */

function displayError(message){

    const panel = getOutputPanel();

    if(panel){

        panel.innerHTML =

        `<span class="text-danger">

${message}

</span>`;

    }

}

/* ==========================================================
   LOADING
   ========================================================== */

function showEditorLoading(){

    document

    .getElementById("editorLoading")

    ?.classList.remove("d-none");

}

function hideEditorLoading(){

    document

    .getElementById("editorLoading")

    ?.classList.add("d-none");

}

/* ==========================================================
   HELPERS
   ========================================================== */

function getProblemId(){

    return document

    .getElementById("problemId")

    ?.value || "";

}

function getCustomInput(){

    return document

    .getElementById("customInput")

    ?.value || "";

}

/* ==========================================================
   AUTO SAVE
   ========================================================== */

setInterval(()=>{

    if(MonacoApp.autoSave){

        saveDraft();

    }

},30000);

/* ==========================================================
   BUTTON EVENTS
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        document.getElementById("runCodeBtn")

        ?.addEventListener(

            "click",

            runCode

        );

        document.getElementById("submitCodeBtn")

        ?.addEventListener(

            "click",

            submitCode

        );

    }

);
/* ==========================================================
   PART 4
   THEMES • KEYBOARD SHORTCUTS • FORMATTING
   FIND & REPLACE • EDITOR COMMANDS
   ========================================================== */

"use strict";

/* ==========================================================
   CUSTOM THEMES
   ========================================================== */

function defineCustomThemes(){

    if(typeof monaco === "undefined") return;

    monaco.editor.defineTheme("lab-dark",{

        base:"vs-dark",

        inherit:true,

        rules:[

            {token:"comment",foreground:"6A9955"},
            {token:"keyword",foreground:"569CD6"},
            {token:"string",foreground:"CE9178"},
            {token:"number",foreground:"B5CEA8"}

        ],

        colors:{

            "editor.background":"#0F172A",

            "editor.lineHighlightBackground":"#1E293B",

            "editorCursor.foreground":"#38BDF8",

            "editor.selectionBackground":"#264F78"

        }

    });

    monaco.editor.defineTheme("lab-light",{

        base:"vs",

        inherit:true,

        rules:[],

        colors:{

            "editor.background":"#FFFFFF"

        }

    });

}

/* ==========================================================
   APPLY THEME
   ========================================================== */

function applyEditorTheme(theme){

    MonacoApp.currentTheme = theme;

    monaco.editor.setTheme(theme);

    localStorage.setItem(

        "editor_theme",

        theme

    );

}

/* ==========================================================
   TOGGLE THEME
   ========================================================== */

function toggleEditorTheme(){

    if(MonacoApp.currentTheme==="lab-dark"){

        applyEditorTheme("lab-light");

    }

    else{

        applyEditorTheme("lab-dark");

    }

}

/* ==========================================================
   FORMAT DOCUMENT
   ========================================================== */

async function formatCode(){

    if(!MonacoApp.editor) return;

    await MonacoApp.editor.getAction(

        "editor.action.formatDocument"

    ).run();

}

/* ==========================================================
   FIND
   ========================================================== */

function openFind(){

    MonacoApp.editor.trigger(

        "",

        "actions.find",

        null

    );

}

/* ==========================================================
   REPLACE
   ========================================================== */

function openReplace(){

    MonacoApp.editor.trigger(

        "",

        "editor.action.startFindReplaceAction",

        null

    );

}

/* ==========================================================
   GOTO LINE
   ========================================================== */

function gotoLine(){

    MonacoApp.editor.trigger(

        "",

        "editor.action.gotoLine",

        null

    );

}

/* ==========================================================
   COMMAND PALETTE
   ========================================================== */

function openCommandPalette(){

    MonacoApp.editor.trigger(

        "",

        "editor.action.quickCommand",

        null

    );

}

/* ==========================================================
   ZOOM
   ========================================================== */

function zoomIn(){

    MonacoApp.fontSize++;

    MonacoApp.editor.updateOptions({

        fontSize:MonacoApp.fontSize

    });

}

function zoomOut(){

    if(MonacoApp.fontSize>10){

        MonacoApp.fontSize--;

        MonacoApp.editor.updateOptions({

            fontSize:MonacoApp.fontSize

        });

    }

}

/* ==========================================================
   RESET ZOOM
   ========================================================== */

function resetZoom(){

    MonacoApp.fontSize=16;

    MonacoApp.editor.updateOptions({

        fontSize:16

    });

}

/* ==========================================================
   KEYBOARD SHORTCUTS
   ========================================================== */

function registerKeyboardShortcuts(){

    if(!MonacoApp.editor) return;

    MonacoApp.editor.addCommand(

        monaco.KeyMod.CtrlCmd |

        monaco.KeyCode.Enter,

        ()=>{

            runCode();

        }

    );

    MonacoApp.editor.addCommand(

        monaco.KeyMod.CtrlCmd |

        monaco.KeyCode.KeyS,

        ()=>{

            saveDraft();

        }

    );

    MonacoApp.editor.addCommand(

        monaco.KeyMod.CtrlCmd |

        monaco.KeyMod.Shift |

        monaco.KeyCode.Enter,

        ()=>{

            submitCode();

        }

    );

    MonacoApp.editor.addCommand(

        monaco.KeyMod.Alt |

        monaco.KeyCode.KeyF,

        ()=>{

            formatCode();

        }

    );

}

/* ==========================================================
   LINE NUMBERS
   ========================================================== */

function toggleLineNumbers(){

    const enabled =

        MonacoApp.editor.getRawOptions()

        .lineNumbers !== "off";

    MonacoApp.editor.updateOptions({

        lineNumbers:

            enabled

            ? "off"

            : "on"

    });

}

/* ==========================================================
   MINIMAP
   ========================================================== */

function toggleMinimap(){

    const options =

        MonacoApp.editor.getRawOptions();

    MonacoApp.editor.updateOptions({

        minimap:{

            enabled:

            !options.minimap.enabled

        }

    });

}

/* ==========================================================
   WORD WRAP
   ========================================================== */

function toggleWordWrap(){

    const options =

        MonacoApp.editor.getRawOptions();

    MonacoApp.editor.updateOptions({

        wordWrap:

            options.wordWrap==="on"

            ?"off"

            :"on"

    });

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        setTimeout(()=>{

            defineCustomThemes();

            applyEditorTheme("lab-dark");

            registerKeyboardShortcuts();

        },500);

    }

);
/* ==========================================================
   PART 6
   ERROR MARKERS • DIAGNOSTICS • OUTPUT CONSOLE
   COMPILATION RESULTS • EXECUTION STATUS
   ========================================================== */

"use strict";

/* ==========================================================
   DIAGNOSTICS
   ========================================================== */

const Diagnostics = {

    markers: [],

    output: [],

    lastExecution: null

};

/* ==========================================================
   CLEAR MARKERS
   ========================================================== */

function clearMarkers(){

    if(!MonacoApp.editor) return;

    const model = MonacoApp.editor.getModel();

    if(!model) return;

    monaco.editor.setModelMarkers(

        model,

        "lab-autograder",

        []

    );

}

/* ==========================================================
   ADD MARKER
   ========================================================== */

function addMarker(

    line,

    column,

    message,

    severity="error"

){

    if(!MonacoApp.editor) return;

    const model = MonacoApp.editor.getModel();

    if(!model) return;

    const severityMap = {

        error: monaco.MarkerSeverity.Error,

        warning: monaco.MarkerSeverity.Warning,

        info: monaco.MarkerSeverity.Info,

        hint: monaco.MarkerSeverity.Hint

    };

    const markers = [

        {

            startLineNumber: line,

            startColumn: column,

            endLineNumber: line,

            endColumn: column + 1,

            message: message,

            severity:

                severityMap[severity]

        }

    ];

    monaco.editor.setModelMarkers(

        model,

        "lab-autograder",

        markers

    );

}

/* ==========================================================
   PARSE COMPILER ERRORS
   ========================================================== */

function parseCompilerErrors(errors){

    clearMarkers();

    if(!errors || !Array.isArray(errors)){

        return;

    }

    errors.forEach(error=>{

        addMarker(

            error.line || 1,

            error.column || 1,

            error.message || "Compilation Error",

            error.type || "error"

        );

    });

}

/* ==========================================================
   OUTPUT CONSOLE
   ========================================================== */

function setConsoleOutput(text){

    const consoleBox =

        document.getElementById(

            "outputConsole"

        );

    if(consoleBox){

        consoleBox.textContent = text;

    }

}

function appendConsole(text){

    const consoleBox =

        document.getElementById(

            "outputConsole"

        );

    if(consoleBox){

        consoleBox.textContent +=

            text + "\n";

    }

}

function clearConsole(){

    setConsoleOutput("");

}

/* ==========================================================
   EXECUTION STATUS
   ========================================================== */

function setExecutionStatus(

    status,

    message

){

    const badge =

        document.getElementById(

            "executionStatus"

        );

    if(!badge) return;

    badge.className =

        `badge bg-${status}`;

    badge.textContent =

        message;

}

/* ==========================================================
   EXECUTION SUMMARY
   ========================================================== */

function updateExecutionSummary(result){

    document.getElementById(

        "executionTime"

    )?.textContent =

        result.execution_time || "0 ms";

    document.getElementById(

        "memoryUsage"

    )?.textContent =

        result.memory || "0 KB";

    document.getElementById(

        "exitCode"

    )?.textContent =

        result.exit_code ?? "0";

}

/* ==========================================================
   HANDLE EXECUTION RESULT
   ========================================================== */

function handleExecutionResult(result){

    Diagnostics.lastExecution = result;

    clearConsole();

    clearMarkers();

    if(result.compile_error){

        setExecutionStatus(

            "danger",

            "Compilation Error"

        );

        parseCompilerErrors(

            result.compile_error.details

        );

        appendConsole(

            result.compile_error.message

        );

        return;

    }

    if(result.runtime_error){

        setExecutionStatus(

            "warning",

            "Runtime Error"

        );

        appendConsole(

            result.runtime_error

        );

        return;

    }

    setExecutionStatus(

        "success",

        "Execution Successful"

    );

    appendConsole(

        result.stdout || ""

    );

    updateExecutionSummary(result);

}

/* ==========================================================
   TEST CASE RESULTS
   ========================================================== */

function renderTestCaseResults(testCases){

    const table =

        document.getElementById(

            "testCaseResults"

        );

    if(!table) return;

    table.innerHTML = "";

    testCases.forEach((test,index)=>{

        const row =

            document.createElement("tr");

        row.innerHTML = `

            <td>${index+1}</td>

            <td>${test.status}</td>

            <td>${test.time}</td>

            <td>${test.memory}</td>

        `;

        table.appendChild(row);

    });

}

/* ==========================================================
   COPY OUTPUT
   ========================================================== */

async function copyConsoleOutput(){

    const consoleBox =

        document.getElementById(

            "outputConsole"

        );

    if(!consoleBox) return;

    try{

        await navigator.clipboard.writeText(

            consoleBox.textContent

        );

        console.log(

            "Console copied."

        );

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   DOWNLOAD OUTPUT
   ========================================================== */

function downloadConsoleOutput(){

    const consoleBox =

        document.getElementById(

            "outputConsole"

        );

    if(!consoleBox) return;

    const blob = new Blob(

        [consoleBox.textContent],

        {

            type:"text/plain"

        }

    );

    const link =

        document.createElement("a");

    link.href =

        URL.createObjectURL(blob);

    link.download =

        "program_output.txt";

    link.click();

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        document.getElementById(

            "copyOutputBtn"

        )?.addEventListener(

            "click",

            copyConsoleOutput

        );

        document.getElementById(

            "downloadOutputBtn"

        )?.addEventListener(

            "click",

            downloadConsoleOutput

        );

    }

);
/* ==========================================================
   PART 7
   FILE UPLOAD • DOWNLOAD • COPY • RESET
   LOCAL STORAGE • SESSION RESTORE
   ========================================================== */

"use strict";

/* ==========================================================
   FILE MANAGER
   ========================================================== */

const FileManager = {

    fileName: "solution",

    extension: ".txt",

    autoBackup: true

};

/* ==========================================================
   FILE EXTENSION
   ========================================================== */

function getFileExtension(){

    switch(MonacoApp.currentLanguage){

        case "python":

            return ".py";

        case "c":

            return ".c";

        case "cpp":

            return ".cpp";

        case "java":

            return ".java";

        case "javascript":

            return ".js";

        default:

            return ".txt";

    }

}

/* ==========================================================
   UPLOAD SOURCE FILE
   ========================================================== */

function uploadSourceFile(event){

    const file = event.target.files[0];

    if(!file) return;

    const reader = new FileReader();

    reader.onload = function(e){

        setCode(e.target.result);

        localStorage.setItem(

            "uploaded_file_name",

            file.name

        );

    };

    reader.readAsText(file);

}

/* ==========================================================
   DOWNLOAD SOURCE
   ========================================================== */

function downloadSourceCode(){

    const code = getCode();

    const blob = new Blob(

        [code],

        {

            type:"text/plain"

        }

    );

    const link = document.createElement("a");

    link.href = URL.createObjectURL(blob);

    link.download =

        FileManager.fileName +

        getFileExtension();

    link.click();

}

/* ==========================================================
   COPY SOURCE
   ========================================================== */

async function copySourceCode(){

    try{

        await navigator.clipboard.writeText(

            getCode()

        );

        console.log(

            "Source copied."

        );

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   RESET SOURCE
   ========================================================== */

function resetSourceCode(){

    if(!confirm(

        "Reset current code?"

    )){

        return;

    }

    loadTemplate(

        MonacoApp.currentLanguage

    );

}

/* ==========================================================
   BACKUP
   ========================================================== */

function backupEditor(){

    if(!FileManager.autoBackup){

        return;

    }

    const backup = {

        language:

            MonacoApp.currentLanguage,

        theme:

            MonacoApp.currentTheme,

        code:

            getCode(),

        timestamp:

            Date.now()

    };

    localStorage.setItem(

        "editor_backup",

        JSON.stringify(backup)

    );

}

/* ==========================================================
   RESTORE BACKUP
   ========================================================== */

function restoreBackup(){

    const backup =

        localStorage.getItem(

            "editor_backup"

        );

    if(!backup){

        return;

    }

    try{

        const data = JSON.parse(backup);

        changeLanguage(

            data.language

        );

        changeTheme(

            data.theme

        );

        setCode(

            data.code

        );

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   CLEAR BACKUP
   ========================================================== */

function clearBackup(){

    localStorage.removeItem(

        "editor_backup"

    );

}

/* ==========================================================
   SESSION SAVE
   ========================================================== */

function saveEditorSession(){

    const session = {

        cursor:

            MonacoApp.editor

            .getPosition(),

        scroll:

            MonacoApp.editor

            .getScrollTop()

    };

    localStorage.setItem(

        "editor_session",

        JSON.stringify(session)

    );

}

/* ==========================================================
   SESSION RESTORE
   ========================================================== */

function restoreEditorSession(){

    const session =

        localStorage.getItem(

            "editor_session"

        );

    if(!session ||

        !MonacoApp.editor){

        return;

    }

    try{

        const data = JSON.parse(session);

        MonacoApp.editor.setPosition(

            data.cursor

        );

        MonacoApp.editor.setScrollTop(

            data.scroll

        );

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   AUTO BACKUP
   ========================================================== */

setInterval(()=>{

    backupEditor();

    saveEditorSession();

},60000);

/* ==========================================================
   FILE EVENTS
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        document

        .getElementById("uploadCode")

        ?.addEventListener(

            "change",

            uploadSourceFile

        );

        document

        .getElementById("downloadCode")

        ?.addEventListener(

            "click",

            downloadSourceCode

        );

        document

        .getElementById("copyCode")

        ?.addEventListener(

            "click",

            copySourceCode

        );

        document

        .getElementById("resetCode")

        ?.addEventListener(

            "click",

            resetSourceCode

        );

        restoreBackup();

        setTimeout(

            restoreEditorSession,

            500

        );

    }

);
/* ==========================================================
   PART 8
   TEST CASES • CUSTOM INPUT • OUTPUT VIEWER
   EXECUTION METRICS • VERDICT PANEL
   ========================================================== */

"use strict";

/* ==========================================================
   EXECUTION DATA
   ========================================================== */

const ExecutionManager = {

    testCases: [],

    customInput: "",

    output: "",

    verdict: "",

    executionTime: 0,

    memory: 0

};

/* ==========================================================
   CUSTOM INPUT
   ========================================================== */

function getCustomInput(){

    return document.getElementById(

        "customInput"

    )?.value || "";

}

function clearCustomInput(){

    const input = document.getElementById(

        "customInput"

    );

    if(input){

        input.value = "";

    }

}

/* ==========================================================
   OUTPUT
   ========================================================== */

function setOutput(output){

    const consoleBox =

        document.getElementById(

            "programOutput"

        );

    if(consoleBox){

        consoleBox.textContent = output;

    }

}

function appendOutput(output){

    const consoleBox =

        document.getElementById(

            "programOutput"

        );

    if(consoleBox){

        consoleBox.textContent +=

            output + "\n";

    }

}

function clearProgramOutput(){

    setOutput("");

}

/* ==========================================================
   VERDICT
   ========================================================== */

function updateVerdict(verdict){

    ExecutionManager.verdict = verdict;

    const badge = document.getElementById(

        "verdictBadge"

    );

    if(!badge) return;

    badge.className =

        "badge";

    switch(verdict){

        case "Accepted":

            badge.classList.add(

                "bg-success"

            );

            break;

        case "Wrong Answer":

            badge.classList.add(

                "bg-danger"

            );

            break;

        case "Compilation Error":

            badge.classList.add(

                "bg-warning"

            );

            break;

        case "Runtime Error":

            badge.classList.add(

                "bg-dark"

            );

            break;

        default:

            badge.classList.add(

                "bg-secondary"

            );

    }

    badge.textContent = verdict;

}

/* ==========================================================
   EXECUTION METRICS
   ========================================================== */

function updateMetrics(result){

    document.getElementById(

        "executionTime"

    )?.textContent =

        result.execution_time + " ms";

    document.getElementById(

        "memoryUsage"

    )?.textContent =

        result.memory + " KB";

}

/* ==========================================================
   TEST CASE TABLE
   ========================================================== */

function renderTestCases(testCases){

    const table = document.getElementById(

        "testCaseTable"

    );

    if(!table) return;

    table.innerHTML = "";

    testCases.forEach((test,index)=>{

        const row = document.createElement("tr");

        row.innerHTML = `

            <td>${index+1}</td>

            <td>${test.status}</td>

            <td>${test.execution_time} ms</td>

            <td>${test.memory} KB</td>

        `;

        table.appendChild(row);

    });

}

/* ==========================================================
   SUMMARY
   ========================================================== */

function updateSummary(testCases){

    const total = testCases.length;

    const passed = testCases.filter(

        t=>t.status==="Passed"

    ).length;

    const failed = total - passed;

    document.getElementById(

        "passedCount"

    )?.textContent = passed;

    document.getElementById(

        "failedCount"

    )?.textContent = failed;

    document.getElementById(

        "totalCount"

    )?.textContent = total;

}

/* ==========================================================
   PROCESS RESULT
   ========================================================== */

function processExecutionResult(result){

    clearProgramOutput();

    setOutput(

        result.output || ""

    );

    updateVerdict(

        result.verdict ||

        "Accepted"

    );

    updateMetrics(result);

    if(result.test_cases){

        renderTestCases(

            result.test_cases

        );

        updateSummary(

            result.test_cases

        );

    }

}

/* ==========================================================
   RUN SAMPLE TESTS
   ========================================================== */

async function runSampleTests(){

    try{

        const response = await fetch(

            "/api/code/test",

            {

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify({

                    code:getCode(),

                    language:MonacoApp.currentLanguage

                })

            }

        );

        const result =

            await response.json();

        processExecutionResult(

            result

        );

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   CLEAR RESULTS
   ========================================================== */

function clearResults(){

    clearProgramOutput();

    updateVerdict("");

    renderTestCases([]);

    updateSummary([]);

}

/* ==========================================================
   DOWNLOAD RESULTS
   ========================================================== */

function downloadResults(){

    const content =

`Verdict : ${ExecutionManager.verdict}

Time : ${document.getElementById("executionTime")?.textContent}

Memory : ${document.getElementById("memoryUsage")?.textContent}

Output:

${document.getElementById("programOutput")?.textContent}`;

    const blob = new Blob(

        [content],

        {

            type:"text/plain"

        }

    );

    const link =

        document.createElement("a");

    link.href =

        URL.createObjectURL(blob);

    link.download =

        "execution_result.txt";

    link.click();

}

/* ==========================================================
   EVENTS
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        document.getElementById(

            "runTestsBtn"

        )?.addEventListener(

            "click",

            runSampleTests

        );

        document.getElementById(

            "clearResultsBtn"

        )?.addEventListener(

            "click",

            clearResults

        );

        document.getElementById(

            "downloadResultsBtn"

        )?.addEventListener(

            "click",

            downloadResults

        );

    }

);
/* ==========================================================
   PART 9
   FULLSCREEN • SPLIT VIEW • MINIMAP
   RESPONSIVE • PERFORMANCE
   ========================================================== */

"use strict";

/* ==========================================================
   EDITOR LAYOUT
   ========================================================== */

const EditorLayout = {

    fullscreen: false,

    splitView: false,

    minimap: true

};

/* ==========================================================
   FULLSCREEN
   ========================================================== */

function toggleFullscreen(){

    const container = document.getElementById("editorContainer");

    if(!container) return;

    if(!document.fullscreenElement){

        container.requestFullscreen();

        EditorLayout.fullscreen = true;

    }else{

        document.exitFullscreen();

        EditorLayout.fullscreen = false;

    }

    setTimeout(layoutEditor,300);

}

/* ==========================================================
   SPLIT VIEW
   ========================================================== */

function toggleSplitView(){

    const editor = document.getElementById("editorPane");

    const output = document.getElementById("outputPane");

    if(!editor || !output) return;

    EditorLayout.splitView = !EditorLayout.splitView;

    if(EditorLayout.splitView){

        editor.classList.add("col-lg-6");

        output.classList.remove("d-none");

        output.classList.add("col-lg-6");

    }else{

        editor.classList.remove("col-lg-6");

        output.classList.add("d-none");

    }

    layoutEditor();

}

/* ==========================================================
   MINIMAP
   ========================================================== */

function toggleMinimap(){

    EditorLayout.minimap = !EditorLayout.minimap;

    if(MonacoApp.editor){

        MonacoApp.editor.updateOptions({

            minimap:{

                enabled:EditorLayout.minimap

            }

        });

    }

}

/* ==========================================================
   LINE HIGHLIGHT
   ========================================================== */

function toggleLineHighlight(){

    if(!MonacoApp.editor) return;

    const options = MonacoApp.editor.getRawOptions();

    MonacoApp.editor.updateOptions({

        renderLineHighlight:

            options.renderLineHighlight === "all"

            ? "none"

            : "all"

    });

}

/* ==========================================================
   WORD WRAP
   ========================================================== */

function toggleWordWrap(){

    if(!MonacoApp.editor) return;

    const options = MonacoApp.editor.getRawOptions();

    MonacoApp.editor.updateOptions({

        wordWrap:

            options.wordWrap === "on"

            ? "off"

            : "on"

    });

}

/* ==========================================================
   LAYOUT
   ========================================================== */

function layoutEditor(){

    if(MonacoApp.editor){

        MonacoApp.editor.layout();

    }

}

/* ==========================================================
   RESPONSIVE
   ========================================================== */

function handleResponsiveEditor(){

    if(window.innerWidth < 768){

        if(MonacoApp.editor){

            MonacoApp.editor.updateOptions({

                minimap:{enabled:false},

                fontSize:14

            });

        }

    }else{

        if(MonacoApp.editor){

            MonacoApp.editor.updateOptions({

                minimap:{

                    enabled:EditorLayout.minimap

                },

                fontSize:MonacoApp.fontSize

            });

        }

    }

}

/* ==========================================================
   PERFORMANCE
   ========================================================== */

function optimizeEditor(){

    if(!MonacoApp.editor) return;

    MonacoApp.editor.updateOptions({

        smoothScrolling:true,

        cursorSmoothCaretAnimation:"on",

        automaticLayout:true,

        renderWhitespace:"selection",

        renderControlCharacters:false,

        renderValidationDecorations:"editable",

        bracketPairColorization:{

            enabled:true

        }

    });

}

/* ==========================================================
   AUTO LAYOUT
   ========================================================== */

window.addEventListener(

    "resize",

    ()=>{

        handleResponsiveEditor();

        layoutEditor();

    }

);

/* ==========================================================
   COPY CURRENT LINE
   ========================================================== */

function copyCurrentLine(){

    if(!MonacoApp.editor) return;

    const position = MonacoApp.editor.getPosition();

    const model = MonacoApp.editor.getModel();

    const line = model.getLineContent(

        position.lineNumber

    );

    navigator.clipboard.writeText(line);

}

/* ==========================================================
   DUPLICATE LINE
   ========================================================== */

function duplicateCurrentLine(){

    if(!MonacoApp.editor) return;

    MonacoApp.editor.trigger(

        "",

        "editor.action.copyLinesDownAction",

        null

    );

}

/* ==========================================================
   MOVE LINE
   ========================================================== */

function moveLineUp(){

    MonacoApp.editor.trigger(

        "",

        "editor.action.moveLinesUpAction",

        null

    );

}

function moveLineDown(){

    MonacoApp.editor.trigger(

        "",

        "editor.action.moveLinesDownAction",

        null

    );

}

/* ==========================================================
   CURSOR POSITION
   ========================================================== */

function updateCursorStatus(){

    if(!MonacoApp.editor) return;

    MonacoApp.editor.onDidChangeCursorPosition(

        event=>{

            const label = document.getElementById(

                "cursorPosition"

            );

            if(label){

                label.textContent =

                    `Ln ${event.position.lineNumber}, Col ${event.position.column}`;

            }

        }

    );

}

/* ==========================================================
   STATUS BAR
   ========================================================== */

function updateStatusBar(){

    const language = document.getElementById("statusLanguage");

    const encoding = document.getElementById("statusEncoding");

    if(language){

        language.textContent = MonacoApp.currentLanguage.toUpperCase();

    }

    if(encoding){

        encoding.textContent = "UTF-8";

    }

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        setTimeout(()=>{

            optimizeEditor();

            handleResponsiveEditor();

            updateCursorStatus();

            updateStatusBar();

        },500);

    }

);
/* ==========================================================
   PART 10
   BOOTSTRAP • API WRAPPER • UTILITIES
   ERROR HANDLING • FINAL INITIALIZATION
   ========================================================== */

"use strict";

/* ==========================================================
   VERSION
   ========================================================== */

const MONACO_VERSION = "1.0.0";

/* ==========================================================
   API WRAPPER
   ========================================================== */

async function editorApi(url, options = {}){

    const config = {

        headers:{
            "Content-Type":"application/json",
            ...(options.headers || {})
        },

        ...options

    };

    try{

        const response = await fetch(url, config);

        if(!response.ok){

            throw new Error(

                `HTTP ${response.status}`

            );

        }

        return await response.json();

    }

    catch(error){

        console.error(error);

        showEditorMessage(

            "Unable to connect to server.",

            "danger"

        );

        return null;

    }

}

/* ==========================================================
   MESSAGE
   ========================================================== */

function showEditorMessage(

    message,

    type="info"

){

    const container =

        document.getElementById(

            "editorMessage"

        );

    if(!container){

        console.log(message);

        return;

    }

    container.innerHTML =

    `<div class="alert alert-${type} alert-dismissible fade show">

        ${message}

        <button

            class="btn-close"

            data-bs-dismiss="alert">

        </button>

    </div>`;

}

/* ==========================================================
   LOADING
   ========================================================== */

function showLoadingOverlay(){

    document

    .getElementById("loadingOverlay")

    ?.classList.remove("d-none");

}

function hideLoadingOverlay(){

    document

    .getElementById("loadingOverlay")

    ?.classList.add("d-none");

}

/* ==========================================================
   BOOTSTRAP
   ========================================================== */

function initializeBootstrap(){

    if(typeof bootstrap==="undefined"){

        return;

    }

    document

    .querySelectorAll(

        '[data-bs-toggle="tooltip"]'

    )

    .forEach(el=>{

        new bootstrap.Tooltip(el);

    });

    document

    .querySelectorAll(

        '[data-bs-toggle="popover"]'

    )

    .forEach(el=>{

        new bootstrap.Popover(el);

    });

}

/* ==========================================================
   SESSION
   ========================================================== */

function saveSession(){

    const data = {

        language:

            MonacoApp.currentLanguage,

        theme:

            MonacoApp.currentTheme,

        code:

            getCode()

    };

    localStorage.setItem(

        "monaco_session",

        JSON.stringify(data)

    );

}

function restoreSession(){

    const session =

        localStorage.getItem(

            "monaco_session"

        );

    if(!session) return;

    try{

        const data = JSON.parse(session);

        changeLanguage(

            data.language

        );

        changeTheme(

            data.theme

        );

        setCode(

            data.code

        );

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   CLEAR SESSION
   ========================================================== */

function clearSession(){

    localStorage.removeItem(

        "monaco_session"

    );

}

/* ==========================================================
   UTILITIES
   ========================================================== */

function getSelectedText(){

    if(!MonacoApp.editor){

        return "";

    }

    return MonacoApp.editor

        .getModel()

        .getValueInRange(

            MonacoApp.editor

            .getSelection()

        );

}

function insertText(text){

    MonacoApp.editor.executeEdits(

        "",

        [{

            range:

                MonacoApp.editor.getSelection(),

            text:text

        }]

    );

}

/* ==========================================================
   PRINT VERSION
   ========================================================== */

function printVersion(){

    console.log(

`%cLab Auto Grader Monaco Editor v${MONACO_VERSION}`,

"color:#2563eb;font-size:14px;font-weight:bold;"

    );

}

/* ==========================================================
   GLOBAL ERROR HANDLING
   ========================================================== */

window.addEventListener(

    "error",

    event=>{

        console.error(

            "Editor Error:",

            event.error

        );

    }

);

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
   BEFORE UNLOAD
   ========================================================== */

window.addEventListener(

    "beforeunload",

    ()=>{

        saveSession();

        saveCode();

    }

);

/* ==========================================================
   FINAL INITIALIZATION
   ========================================================== */

function initializeEditorApplication(){

    initializeBootstrap();

    restoreSession();

    printVersion();

    console.log(

        "Monaco Editor Ready."

    );

}

/* ==========================================================
   DOM READY
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        setTimeout(

            initializeEditorApplication,

            700

        );

    }

);

/* ==========================================================
   GLOBAL EXPORTS
   ========================================================== */

window.MonacoEditor = {

    editor:()=>MonacoApp.editor,

    run:runCode,

    submit:submitCode,

    save:saveDraft,

    reset:resetSourceCode,

    format:formatCode,

    changeLanguage,

    changeTheme,

    toggleFullscreen,

    toggleMinimap,

    toggleWordWrap,

    download:downloadSourceCode,

    upload:uploadSourceFile,

    copy:copySourceCode,

    clear:clearEditor,

    getCode,

    setCode,

    getSelectedText,

    insertText,

    showMessage:showEditorMessage

};

/* ==========================================================
   END OF MONACO.JS
   ========================================================== */