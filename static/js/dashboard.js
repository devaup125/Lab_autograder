/* ==========================================================
   LAB AUTO GRADER
   Dashboard JavaScript
   Part 1
   ========================================================== */

"use strict";

/* ==========================================================
   DASHBOARD OBJECT
   ========================================================== */

const Dashboard = {

    sidebarOpen: true,

    darkMode: false,

    currentPage: 1,

    refreshInterval: null,

    storage: window.localStorage

};

/* ==========================================================
   DOM ELEMENTS
   ========================================================== */

const dashboard = {

    sidebar: document.getElementById("sidebar"),

    sidebarToggle: document.getElementById("sidebarToggle"),

    themeToggle: document.getElementById("themeToggle"),

    content: document.getElementById("dashboardContent"),

    navbar: document.getElementById("dashboardNavbar"),

    search: document.getElementById("searchInput"),

    toastContainer: document.getElementById("toastContainer")

};

/* ==========================================================
   DOM READY
   ========================================================== */

document.addEventListener("DOMContentLoaded", () => {

    initializeDashboard();

});

/* ==========================================================
   INITIALIZATION
   ========================================================== */

function initializeDashboard(){

    restoreTheme();

    restoreSidebar();

    bindDashboardEvents();

    initializeTooltips();

}

/* ==========================================================
   EVENT BINDING
   ========================================================== */

function bindDashboardEvents(){

    if(dashboard.sidebarToggle){

        dashboard.sidebarToggle.addEventListener(

            "click",

            toggleSidebar

        );

    }

    if(dashboard.themeToggle){

        dashboard.themeToggle.addEventListener(

            "click",

            toggleTheme

        );

    }

    if(dashboard.search){

        dashboard.search.addEventListener(

            "input",

            debounce(handleSearch,300)

        );

    }

}

/* ==========================================================
   SIDEBAR
   ========================================================== */

function toggleSidebar(){

    if(!dashboard.sidebar) return;

    dashboard.sidebar.classList.toggle("collapsed");

    Dashboard.sidebarOpen =

        !dashboard.sidebar.classList.contains("collapsed");

    save(

        "dashboardSidebar",

        Dashboard.sidebarOpen

    );

}

function restoreSidebar(){

    const state = load(

        "dashboardSidebar"

    );

    if(state === false){

        dashboard.sidebar?.classList.add(

            "collapsed"

        );

        Dashboard.sidebarOpen = false;

    }

}

/* ==========================================================
   THEME
   ========================================================== */

function toggleTheme(){

    document.body.classList.toggle("dark-mode");

    Dashboard.darkMode =

        document.body.classList.contains("dark-mode");

    save(

        "dashboardTheme",

        Dashboard.darkMode

    );

}

function restoreTheme(){

    if(load("dashboardTheme")){

        document.body.classList.add(

            "dark-mode"

        );

        Dashboard.darkMode = true;

    }

}

/* ==========================================================
   SEARCH
   ========================================================== */

function handleSearch(event){

    const keyword =

        event.target.value.toLowerCase();

    console.log(

        "Searching:",

        keyword

    );

}

/* ==========================================================
   TOOLTIPS
   ========================================================== */

function initializeTooltips(){

    if(typeof bootstrap === "undefined"){

        return;

    }

    document

    .querySelectorAll(

        '[data-bs-toggle="tooltip"]'

    )

    .forEach(element=>{

        new bootstrap.Tooltip(element);

    });

}

/* ==========================================================
   TOAST
   ========================================================== */

function showToast(

    title,

    message,

    type="info"

){

    if(!dashboard.toastContainer){

        console.log(title,message);

        return;

    }

    const toast=document.createElement("div");

    toast.className=

        `dashboard-toast toast-${type}`;

    toast.innerHTML=`

        <div class="toast-header">

            <strong>${title}</strong>

            <button class="btn-close"></button>

        </div>

        <div class="toast-body">

            ${message}

        </div>

    `;

    dashboard.toastContainer.appendChild(

        toast

    );

    toast.querySelector(".btn-close")

    ?.addEventListener(

        "click",

        ()=>toast.remove()

    );

    setTimeout(

        ()=>toast.remove(),

        5000

    );

}

/* ==========================================================
   LOCAL STORAGE
   ========================================================== */

function save(key,value){

    Dashboard.storage.setItem(

        key,

        JSON.stringify(value)

    );

}

function load(key){

    const value=

        Dashboard.storage.getItem(key);

    return value

        ?JSON.parse(value)

        :null;

}

function remove(key){

    Dashboard.storage.removeItem(key);

}

/* ==========================================================
   UTILITIES
   ========================================================== */

function byId(id){

    return document.getElementById(id);

}

function show(element){

    if(element){

        element.style.display="";

    }

}

function hide(element){

    if(element){

        element.style.display="none";

    }

}

function enable(element){

    if(element){

        element.disabled=false;

    }

}

function disable(element){

    if(element){

        element.disabled=true;

    }

}

/* ==========================================================
   DEBOUNCE
   ========================================================== */

function debounce(callback,delay=300){

    let timer;

    return (...args)=>{

        clearTimeout(timer);

        timer=setTimeout(

            ()=>callback(...args),

            delay

        );

    };

}

/* ==========================================================
   PLACEHOLDERS
   ========================================================== */

function refreshDashboard(){}

function loadDashboardData(){}

function updateDashboard(){}
/* ==========================================================
   PART 2
   DASHBOARD STATISTICS • COUNTERS • PROGRESS
   CHART INITIALIZATION
   ========================================================== */

/* ==========================================================
   COUNTER ANIMATION
   ========================================================== */

function animateCounter(element, target, duration = 1500){

    if(!element) return;

    let start = 0;

    const increment = target / (duration / 16);

    function update(){

        start += increment;

        if(start >= target){

            element.textContent = target.toLocaleString();

            return;

        }

        element.textContent = Math.floor(start).toLocaleString();

        requestAnimationFrame(update);

    }

    update();

}

/* ==========================================================
   INITIALIZE COUNTERS
   ========================================================== */

function initializeCounters(){

    document.querySelectorAll("[data-counter]")

    .forEach(counter=>{

        const target = parseInt(

            counter.dataset.counter || 0

        );

        animateCounter(counter, target);

    });

}

/* ==========================================================
   PROGRESS BAR
   ========================================================== */

function animateProgressBar(bar, value){

    if(!bar) return;

    bar.style.width = "0%";

    setTimeout(()=>{

        bar.style.width = value + "%";

    },100);

}

function initializeProgressBars(){

    document.querySelectorAll("[data-progress]")

    .forEach(bar=>{

        animateProgressBar(

            bar,

            parseInt(bar.dataset.progress)

        );

    });

}

/* ==========================================================
   DASHBOARD CARDS
   ========================================================== */

function initializeDashboardCards(){

    document.querySelectorAll(".dashboard-card")

    .forEach(card=>{

        card.addEventListener("mouseenter",()=>{

            card.classList.add("shadow-lg");

        });

        card.addEventListener("mouseleave",()=>{

            card.classList.remove("shadow-lg");

        });

    });

}

/* ==========================================================
   CHART.JS INITIALIZATION
   ========================================================== */

let dashboardCharts = {};

function initializeCharts(){

    if(typeof Chart === "undefined"){

        console.warn("Chart.js not loaded.");

        return;

    }

    const submissionsCanvas = byId("submissionChart");

    if(submissionsCanvas){

        dashboardCharts.submission = new Chart(

            submissionsCanvas,

            {

                type:"line",

                data:{

                    labels:["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],

                    datasets:[{

                        label:"Submissions",

                        data:[12,18,10,20,28,24,30],

                        borderColor:"#2563eb",

                        backgroundColor:"rgba(37,99,235,.15)",

                        fill:true,

                        tension:.35

                    }]

                },

                options:{

                    responsive:true,

                    maintainAspectRatio:false

                }

            }

        );

    }

    const languageCanvas = byId("languageChart");

    if(languageCanvas){

        dashboardCharts.language = new Chart(

            languageCanvas,

            {

                type:"doughnut",

                data:{

                    labels:[

                        "Python",

                        "C",

                        "C++",

                        "Java"

                    ],

                    datasets:[{

                        data:[40,20,25,15],

                        backgroundColor:[

                            "#2563eb",

                            "#16a34a",

                            "#f59e0b",

                            "#dc2626"

                        ]

                    }]

                },

                options:{

                    responsive:true,

                    maintainAspectRatio:false

                }

            }

        );

    }

}

/* ==========================================================
   UPDATE CHART
   ========================================================== */

function updateSubmissionChart(values){

    if(!dashboardCharts.submission) return;

    dashboardCharts.submission.data.datasets[0].data = values;

    dashboardCharts.submission.update();

}

/* ==========================================================
   DASHBOARD STATISTICS
   ========================================================== */

async function loadDashboardStatistics(){

    try{

        const response = await fetch(

            "/api/dashboard/stats"

        );

        if(!response.ok){

            return;

        }

        const stats = await response.json();

        updateStatistics(stats);

    }

    catch(error){

        console.error(error);

    }

}

function updateStatistics(stats){

    const mapping = {

        totalStudents:"totalStudents",

        totalTeachers:"totalTeachers",

        totalAssignments:"totalAssignments",

        totalSubmissions:"totalSubmissions"

    };

    Object.keys(mapping).forEach(key=>{

        const element = byId(key);

        if(element && stats[mapping[key]] !== undefined){

            animateCounter(

                element,

                stats[mapping[key]]

            );

        }

    });

}

/* ==========================================================
   LIVE DASHBOARD REFRESH
   ========================================================== */

function startDashboardRefresh(){

    Dashboard.refreshInterval = setInterval(()=>{

        loadDashboardStatistics();

    },60000);

}

function stopDashboardRefresh(){

    clearInterval(

        Dashboard.refreshInterval

    );

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        initializeCounters();

        initializeProgressBars();

        initializeDashboardCards();

        initializeCharts();

        loadDashboardStatistics();

        startDashboardRefresh();

    }

);

/* ==========================================================
   PART 3
   NOTIFICATIONS • ACTIVITY FEED • ALERTS
   RECENT EVENTS • LIVE UPDATES
   ========================================================== */

/* ==========================================================
   NOTIFICATION OBJECT
   ========================================================== */

const NotificationCenter = {

    notifications: [],

    unread: 0,

    polling: null

};

/* ==========================================================
   LOAD NOTIFICATIONS
   ========================================================== */

async function loadNotifications(){

    try{

        const response = await fetch(

            "/api/notifications"

        );

        if(!response.ok){

            return;

        }

        const data = await response.json();

        NotificationCenter.notifications =

            data.notifications || [];

        NotificationCenter.unread =

            data.unread || 0;

        renderNotifications();

        updateNotificationBadge();

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   RENDER NOTIFICATIONS
   ========================================================== */

function renderNotifications(){

    const container = byId(

        "notificationList"

    );

    if(!container) return;

    container.innerHTML = "";

    if(

        NotificationCenter.notifications.length === 0

    ){

        container.innerHTML =

        `<div class="text-center p-3 text-muted">

            No notifications available.

        </div>`;

        return;

    }

    NotificationCenter.notifications.forEach(item=>{

        const div = document.createElement("div");

        div.className =

            "notification-item";

        div.innerHTML = `

            <div class="fw-bold">

                ${item.title}

            </div>

            <div class="small text-muted">

                ${item.message}

            </div>

            <div class="text-end">

                <small>${item.time}</small>

            </div>

        `;

        container.appendChild(div);

    });

}

/* ==========================================================
   BADGE
   ========================================================== */

function updateNotificationBadge(){

    const badge = byId(

        "notificationBadge"

    );

    if(!badge) return;

    badge.textContent =

        NotificationCenter.unread;

    badge.style.display =

        NotificationCenter.unread > 0

        ? "inline-block"

        : "none";

}

/* ==========================================================
   MARK ALL READ
   ========================================================== */

async function markNotificationsRead(){

    try{

        await fetch(

            "/api/notifications/read",

            {

                method:"POST"

            }

        );

        NotificationCenter.unread = 0;

        updateNotificationBadge();

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   ACTIVITY FEED
   ========================================================== */

async function loadActivityFeed(){

    try{

        const response = await fetch(

            "/api/activity"

        );

        if(!response.ok){

            return;

        }

        const activities =

            await response.json();

        renderActivityFeed(

            activities

        );

    }

    catch(error){

        console.error(error);

    }

}

function renderActivityFeed(list){

    const container = byId(

        "activityFeed"

    );

    if(!container) return;

    container.innerHTML = "";

    list.forEach(activity=>{

        const item = document.createElement("div");

        item.className =

            "activity-item";

        item.innerHTML = `

            <div class="fw-semibold">

                ${activity.user}

            </div>

            <div>

                ${activity.action}

            </div>

            <small class="text-muted">

                ${activity.time}

            </small>

        `;

        container.appendChild(item);

    });

}

/* ==========================================================
   RECENT SUBMISSIONS
   ========================================================== */

async function loadRecentSubmissions(){

    try{

        const response = await fetch(

            "/api/recent-submissions"

        );

        if(!response.ok){

            return;

        }

        const submissions =

            await response.json();

        renderRecentSubmissions(

            submissions

        );

    }

    catch(error){

        console.error(error);

    }

}

function renderRecentSubmissions(list){

    const table = byId(

        "recentSubmissionTable"

    );

    if(!table) return;

    table.innerHTML = "";

    list.forEach(item=>{

        const row = document.createElement("tr");

        row.innerHTML = `

            <td>${item.student}</td>

            <td>${item.assignment}</td>

            <td>${item.language}</td>

            <td>${item.score}</td>

            <td>${item.time}</td>

        `;

        table.appendChild(row);

    });

}

/* ==========================================================
   ALERTS
   ========================================================== */

function showDashboardAlert(

    message,

    type="info"

){

    const container = byId(

        "dashboardAlert"

    );

    if(!container) return;

    container.innerHTML = `

        <div class="alert alert-${type} alert-dismissible fade show">

            ${message}

            <button

                type="button"

                class="btn-close"

                data-bs-dismiss="alert">

            </button>

        </div>

    `;

}

/* ==========================================================
   LIVE POLLING
   ========================================================== */

function startNotificationPolling(){

    NotificationCenter.polling =

        setInterval(()=>{

            loadNotifications();

            loadActivityFeed();

        },30000);

}

function stopNotificationPolling(){

    clearInterval(

        NotificationCenter.polling

    );

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        loadNotifications();

        loadActivityFeed();

        loadRecentSubmissions();

        startNotificationPolling();

        byId("markAllRead")

        ?.addEventListener(

            "click",

            markNotificationsRead

        );

    }

);
/* ==========================================================
   PART 4
   SEARCH • FILTERS • SORTING • PAGINATION
   TABLE MANAGEMENT
   ========================================================== */

"use strict";

/* ==========================================================
   TABLE MANAGER
   ========================================================== */

const TableManager = {

    currentPage: 1,

    rowsPerPage: 10,

    sortColumn: null,

    sortDirection: "asc",

    rows: []

};

/* ==========================================================
   INITIALIZE TABLES
   ========================================================== */

function initializeTables(){

    document.querySelectorAll(".data-table")

    .forEach(table=>{

        initializeTable(table);

    });

}

function initializeTable(table){

    const headers = table.querySelectorAll("th[data-sort]");

    headers.forEach(header=>{

        header.style.cursor = "pointer";

        header.addEventListener(

            "click",

            ()=>{

                sortTable(

                    table,

                    header.dataset.sort

                );

            }

        );

    });

}

/* ==========================================================
   GLOBAL SEARCH
   ========================================================== */

function searchTable(inputId, tableId){

    const input = byId(inputId);

    const table = byId(tableId);

    if(!input || !table) return;

    const filter = input.value.toLowerCase();

    const rows = table.querySelectorAll("tbody tr");

    rows.forEach(row=>{

        const text = row.textContent.toLowerCase();

        row.style.display =

            text.includes(filter)

            ? ""

            : "none";

    });

}

/* ==========================================================
   SORT TABLE
   ========================================================== */

function sortTable(table, column){

    const tbody = table.querySelector("tbody");

    if(!tbody) return;

    const rows = Array.from(

        tbody.querySelectorAll("tr")

    );

    const headers = Array.from(

        table.querySelectorAll("th")

    );

    const index = headers.findIndex(

        th=>th.dataset.sort === column

    );

    if(index === -1) return;

    TableManager.sortDirection =

        TableManager.sortDirection === "asc"

        ? "desc"

        : "asc";

    rows.sort((a,b)=>{

        const first =

            a.children[index].textContent.trim();

        const second =

            b.children[index].textContent.trim();

        if(TableManager.sortDirection === "asc"){

            return first.localeCompare(

                second,

                undefined,

                {numeric:true}

            );

        }

        return second.localeCompare(

            first,

            undefined,

            {numeric:true}

        );

    });

    tbody.innerHTML = "";

    rows.forEach(row=>{

        tbody.appendChild(row);

    });

}

/* ==========================================================
   FILTER
   ========================================================== */

function filterTable(selectId, tableId, column){

    const select = byId(selectId);

    const table = byId(tableId);

    if(!select || !table) return;

    const value =

        select.value.toLowerCase();

    table.querySelectorAll("tbody tr")

    .forEach(row=>{

        const cell =

            row.children[column]

            .textContent

            .toLowerCase();

        row.style.display =

            value === "all" ||

            cell.includes(value)

            ? ""

            : "none";

    });

}

/* ==========================================================
   PAGINATION
   ========================================================== */

function paginateTable(tableId, page){

    const table = byId(tableId);

    if(!table) return;

    const rows = Array.from(

        table.querySelectorAll("tbody tr")

    );

    const start =

        (page - 1) *

        TableManager.rowsPerPage;

    const end =

        start +

        TableManager.rowsPerPage;

    rows.forEach((row,index)=>{

        row.style.display =

            index >= start && index < end

            ? ""

            : "none";

    });

    TableManager.currentPage = page;

}

function nextPage(tableId){

    paginateTable(

        tableId,

        TableManager.currentPage + 1

    );

}

function previousPage(tableId){

    if(TableManager.currentPage > 1){

        paginateTable(

            tableId,

            TableManager.currentPage - 1

        );

    }

}

/* ==========================================================
   SELECT ALL
   ========================================================== */

function toggleSelectAll(masterId, tableId){

    const master = byId(masterId);

    const table = byId(tableId);

    if(!master || !table) return;

    table.querySelectorAll(

        "tbody input[type='checkbox']"

    )

    .forEach(box=>{

        box.checked = master.checked;

    });

}

/* ==========================================================
   SELECTED ROWS
   ========================================================== */

function getSelectedRows(tableId){

    const table = byId(tableId);

    if(!table) return [];

    return Array.from(

        table.querySelectorAll(

            "tbody input[type='checkbox']:checked"

        )

    );

}

/* ==========================================================
   DELETE SELECTED
   ========================================================== */

function deleteSelectedRows(tableId){

    const selected =

        getSelectedRows(tableId);

    if(selected.length === 0){

        showToast(

            "No Selection",

            "Please select at least one row.",

            "warning"

        );

        return;

    }

    if(!confirm(

        `Delete ${selected.length} selected rows?`

    )){

        return;

    }

    selected.forEach(box=>{

        box.closest("tr")?.remove();

    });

    showToast(

        "Success",

        "Selected rows deleted.",

        "success"

    );

}

/* ==========================================================
   EXPORT TABLE TO CSV
   ========================================================== */

function exportTableCSV(tableId, filename="table.csv"){

    const table = byId(tableId);

    if(!table) return;

    let csv = [];

    table.querySelectorAll("tr")

    .forEach(row=>{

        let cols = [];

        row.querySelectorAll("th,td")

        .forEach(cell=>{

            cols.push(

                `"${cell.innerText}"`

            );

        });

        csv.push(

            cols.join(",")

        );

    });

    const blob = new Blob(

        [csv.join("\n")],

        {

            type:"text/csv"

        }

    );

    const link =

        document.createElement("a");

    link.href =

        URL.createObjectURL(blob);

    link.download = filename;

    link.click();

}

/* ==========================================================
   REFRESH TABLE
   ========================================================== */

function refreshTable(tableId){

    showToast(

        "Refreshing",

        "Updating table data...",

        "info"

    );

    console.log(

        "Refresh:",

        tableId

    );

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        initializeTables();

    }

);
/* ==========================================================
   PART 5
   STUDENT DASHBOARD
   ASSIGNMENTS • SUBMISSIONS • CALENDAR • DEADLINES
   ========================================================== */

"use strict";

/* ==========================================================
   STUDENT DASHBOARD OBJECT
   ========================================================== */

const StudentDashboard = {

    assignments: [],

    submissions: [],

    deadlines: [],

    calendarEvents: []

};

/* ==========================================================
   LOAD STUDENT DASHBOARD
   ========================================================== */

async function loadStudentDashboard(){

    try{

        const response = await fetch(

            "/api/student/dashboard"

        );

        if(!response.ok){

            return;

        }

        const data = await response.json();

        StudentDashboard.assignments =

            data.assignments || [];

        StudentDashboard.submissions =

            data.submissions || [];

        StudentDashboard.deadlines =

            data.deadlines || [];

        renderAssignments();

        renderSubmissionStatus();

        renderUpcomingDeadlines();

        updateStudentSummary(data);

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   ASSIGNMENT CARDS
   ========================================================== */

function renderAssignments(){

    const container = byId(

        "assignmentContainer"

    );

    if(!container) return;

    container.innerHTML = "";

    StudentDashboard.assignments.forEach(item=>{

        const card = document.createElement("div");

        card.className = "assignment-card card mb-3";

        card.innerHTML = `

            <div class="card-body">

                <h5>${item.title}</h5>

                <p>${item.description}</p>

                <div class="d-flex justify-content-between">

                    <span class="badge bg-primary">

                        ${item.language}

                    </span>

                    <span>

                        Due: ${item.deadline}

                    </span>

                </div>

            </div>

        `;

        container.appendChild(card);

    });

}

/* ==========================================================
   SUBMISSION STATUS
   ========================================================== */

function renderSubmissionStatus(){

    const table = byId(

        "submissionStatusTable"

    );

    if(!table) return;

    table.innerHTML = "";

    StudentDashboard.submissions.forEach(item=>{

        const row = document.createElement("tr");

        row.innerHTML = `

            <td>${item.assignment}</td>

            <td>${item.language}</td>

            <td>${item.score}</td>

            <td>

                <span class="badge bg-${statusColor(item.status)}">

                    ${item.status}

                </span>

            </td>

        `;

        table.appendChild(row);

    });

}

function statusColor(status){

    switch(status.toLowerCase()){

        case "accepted":

            return "success";

        case "pending":

            return "warning";

        case "failed":

            return "danger";

        default:

            return "secondary";

    }

}

/* ==========================================================
   UPCOMING DEADLINES
   ========================================================== */

function renderUpcomingDeadlines(){

    const container = byId(

        "deadlineList"

    );

    if(!container) return;

    container.innerHTML = "";

    StudentDashboard.deadlines.forEach(item=>{

        const li = document.createElement("li");

        li.className =

            "list-group-item d-flex justify-content-between";

        li.innerHTML = `

            <span>${item.assignment}</span>

            <strong>${item.date}</strong>

        `;

        container.appendChild(li);

    });

}

/* ==========================================================
   STUDENT SUMMARY
   ========================================================== */

function updateStudentSummary(data){

    byId("studentAssignments")

    ?.textContent =

        data.totalAssignments || 0;

    byId("studentCompleted")

    ?.textContent =

        data.completed || 0;

    byId("studentPending")

    ?.textContent =

        data.pending || 0;

    byId("studentAverage")

    ?.textContent =

        `${data.average || 0}%`;

}

/* ==========================================================
   CALENDAR
   ========================================================== */

function initializeCalendar(){

    const calendar = byId(

        "studentCalendar"

    );

    if(!calendar) return;

    const today = new Date();

    calendar.innerHTML =

        `<strong>${today.toDateString()}</strong>`;

}

/* ==========================================================
   QUICK ACTIONS
   ========================================================== */

function continueAssignment(id){

    window.location.href =

        `/student/assignment/${id}`;

}

function viewSubmission(id){

    window.location.href =

        `/student/submission/${id}`;

}

/* ==========================================================
   PROGRESS
   ========================================================== */

function updateStudentProgress(){

    const progress = byId(

        "studentProgress"

    );

    if(!progress) return;

    const total =

        StudentDashboard.assignments.length;

    const completed =

        StudentDashboard.submissions.filter(

            item=>item.status==="Accepted"

        ).length;

    const percent =

        total===0

        ?0

        :Math.round(

            completed*100/total

        );

    progress.style.width =

        percent + "%";

    progress.textContent =

        percent + "%";

}

/* ==========================================================
   REFRESH
   ========================================================== */

function refreshStudentDashboard(){

    loadStudentDashboard();

    showToast(

        "Updated",

        "Student dashboard refreshed.",

        "success"

    );

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        initializeCalendar();

        loadStudentDashboard();

        setTimeout(

            updateStudentProgress,

            500

        );

    }

);

/* ==========================================================
   PART 6
   TEACHER DASHBOARD
   ASSIGNMENT MANAGEMENT • EVALUATION • LEADERBOARD
   ========================================================== */

"use strict";

/* ==========================================================
   TEACHER DASHBOARD
   ========================================================== */

const TeacherDashboard = {

    assignments: [],

    submissions: [],

    leaderboard: [],

    reports: []

};

/* ==========================================================
   LOAD TEACHER DASHBOARD
   ========================================================== */

async function loadTeacherDashboard(){

    try{

        const response = await fetch(

            "/api/teacher/dashboard"

        );

        if(!response.ok){

            return;

        }

        const data = await response.json();

        TeacherDashboard.assignments =

            data.assignments || [];

        TeacherDashboard.submissions =

            data.submissions || [];

        TeacherDashboard.leaderboard =

            data.leaderboard || [];

        renderTeacherAssignments();

        renderSubmissionQueue();

        renderLeaderboard();

        updateTeacherSummary(data);

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   ASSIGNMENTS
   ========================================================== */

function renderTeacherAssignments(){

    const container = byId(

        "teacherAssignmentList"

    );

    if(!container) return;

    container.innerHTML = "";

    TeacherDashboard.assignments.forEach(item=>{

        const card = document.createElement("div");

        card.className = "card mb-3";

        card.innerHTML = `

            <div class="card-body">

                <h5>${item.title}</h5>

                <p>${item.description}</p>

                <div class="d-flex justify-content-between">

                    <span>${item.language}</span>

                    <span>${item.deadline}</span>

                </div>

            </div>

        `;

        container.appendChild(card);

    });

}

/* ==========================================================
   SUBMISSION QUEUE
   ========================================================== */

function renderSubmissionQueue(){

    const table = byId(

        "evaluationTable"

    );

    if(!table) return;

    table.innerHTML = "";

    TeacherDashboard.submissions.forEach(item=>{

        const row = document.createElement("tr");

        row.innerHTML = `

            <td>${item.student}</td>

            <td>${item.assignment}</td>

            <td>${item.language}</td>

            <td>${item.score}</td>

            <td>

                <button

                    class="btn btn-primary btn-sm"

                    onclick="evaluateSubmission('${item.id}')">

                    Evaluate

                </button>

            </td>

        `;

        table.appendChild(row);

    });

}

/* ==========================================================
   LEADERBOARD
   ========================================================== */

function renderLeaderboard(){

    const body = byId(

        "leaderboardBody"

    );

    if(!body) return;

    body.innerHTML = "";

    TeacherDashboard.leaderboard.forEach((student,index)=>{

        const row = document.createElement("tr");

        row.innerHTML = `

            <td>${index+1}</td>

            <td>${student.name}</td>

            <td>${student.score}</td>

            <td>${student.solved}</td>

        `;

        body.appendChild(row);

    });

}

/* ==========================================================
   SUMMARY
   ========================================================== */

function updateTeacherSummary(data){

    byId("teacherAssignments")

    ?.textContent =

        data.totalAssignments || 0;

    byId("teacherStudents")

    ?.textContent =

        data.totalStudents || 0;

    byId("teacherPending")

    ?.textContent =

        data.pendingEvaluation || 0;

    byId("teacherAverage")

    ?.textContent =

        `${data.averageScore || 0}%`;

}

/* ==========================================================
   EVALUATION
   ========================================================== */

function evaluateSubmission(id){

    window.location.href =

        `/teacher/evaluate/${id}`;

}

async function publishResult(id){

    try{

        const response = await fetch(

            `/api/submission/${id}/publish`,

            {

                method:"POST"

            }

        );

        if(response.ok){

            showToast(

                "Published",

                "Result published successfully.",

                "success"

            );

            loadTeacherDashboard();

        }

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   CREATE ASSIGNMENT
   ========================================================== */

function createAssignment(){

    window.location.href =

        "/teacher/assignment/create";

}

function editAssignment(id){

    window.location.href =

        `/teacher/assignment/${id}/edit`;

}

function deleteAssignment(id){

    if(!confirm(

        "Delete this assignment?"

    )){

        return;

    }

    fetch(

        `/api/assignment/${id}`,

        {

            method:"DELETE"

        }

    )

    .then(()=>{

        showToast(

            "Deleted",

            "Assignment removed.",

            "success"

        );

        loadTeacherDashboard();

    });

}

/* ==========================================================
   REPORTS
   ========================================================== */

async function downloadReport(){

    try{

        const response = await fetch(

            "/api/teacher/report"

        );

        const blob = await response.blob();

        const url =

            URL.createObjectURL(blob);

        const link =

            document.createElement("a");

        link.href = url;

        link.download =

            "teacher-report.pdf";

        link.click();

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   REFRESH
   ========================================================== */

function refreshTeacherDashboard(){

    loadTeacherDashboard();

    showToast(

        "Updated",

        "Teacher dashboard refreshed.",

        "success"

    );

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        loadTeacherDashboard();

    }

);
/* ==========================================================
   PART 7
   ADMIN DASHBOARD
   USER MANAGEMENT • COURSE MANAGEMENT
   SYSTEM STATISTICS • ROLE MANAGEMENT
   ========================================================== */

"use strict";

/* ==========================================================
   ADMIN DASHBOARD OBJECT
   ========================================================== */

const AdminDashboard = {

    users: [],

    courses: [],

    departments: [],

    roles: [],

    statistics: {}

};

/* ==========================================================
   LOAD ADMIN DASHBOARD
   ========================================================== */

async function loadAdminDashboard(){

    try{

        const response = await fetch(

            "/api/admin/dashboard"

        );

        if(!response.ok){

            return;

        }

        const data = await response.json();

        AdminDashboard.users =

            data.users || [];

        AdminDashboard.courses =

            data.courses || [];

        AdminDashboard.departments =

            data.departments || [];

        AdminDashboard.roles =

            data.roles || [];

        AdminDashboard.statistics =

            data.statistics || {};

        renderUsers();

        renderCourses();

        renderDepartments();

        renderRoles();

        updateAdminStatistics();

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   USER MANAGEMENT
   ========================================================== */

function renderUsers(){

    const tbody = byId("userTableBody");

    if(!tbody) return;

    tbody.innerHTML = "";

    AdminDashboard.users.forEach(user=>{

        const row = document.createElement("tr");

        row.innerHTML = `

            <td>${user.id}</td>

            <td>${user.name}</td>

            <td>${user.email}</td>

            <td>${user.role}</td>

            <td>${user.status}</td>

            <td>

                <button

                    class="btn btn-sm btn-primary"

                    onclick="editUser(${user.id})">

                    Edit

                </button>

                <button

                    class="btn btn-sm btn-danger"

                    onclick="deleteUser(${user.id})">

                    Delete

                </button>

            </td>

        `;

        tbody.appendChild(row);

    });

}

function createUser(){

    window.location.href="/admin/users/create";

}

function editUser(id){

    window.location.href=

        `/admin/users/${id}/edit`;

}

async function deleteUser(id){

    if(!confirm("Delete this user?")) return;

    try{

        const response = await fetch(

            `/api/admin/users/${id}`,

            {

                method:"DELETE"

            }

        );

        if(response.ok){

            showToast(

                "Deleted",

                "User removed successfully.",

                "success"

            );

            loadAdminDashboard();

        }

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   COURSE MANAGEMENT
   ========================================================== */

function renderCourses(){

    const table = byId("courseTableBody");

    if(!table) return;

    table.innerHTML = "";

    AdminDashboard.courses.forEach(course=>{

        const row = document.createElement("tr");

        row.innerHTML = `

            <td>${course.code}</td>

            <td>${course.name}</td>

            <td>${course.teacher}</td>

            <td>${course.students}</td>

            <td>

                <button

                    class="btn btn-sm btn-warning"

                    onclick="editCourse('${course.id}')">

                    Edit

                </button>

            </td>

        `;

        table.appendChild(row);

    });

}

function createCourse(){

    window.location.href="/admin/courses/create";

}

function editCourse(id){

    window.location.href=

        `/admin/courses/${id}/edit`;

}

/* ==========================================================
   DEPARTMENT MANAGEMENT
   ========================================================== */

function renderDepartments(){

    const list = byId("departmentList");

    if(!list) return;

    list.innerHTML = "";

    AdminDashboard.departments.forEach(department=>{

        const item = document.createElement("li");

        item.className="list-group-item";

        item.innerHTML=`

            ${department.name}

            <span class="badge bg-primary float-end">

                ${department.students}

            </span>

        `;

        list.appendChild(item);

    });

}

/* ==========================================================
   ROLE MANAGEMENT
   ========================================================== */

function renderRoles(){

    const table = byId("roleTableBody");

    if(!table) return;

    table.innerHTML = "";

    AdminDashboard.roles.forEach(role=>{

        const row = document.createElement("tr");

        row.innerHTML = `

            <td>${role.name}</td>

            <td>${role.permissions}</td>

            <td>

                <button

                    class="btn btn-sm btn-secondary"

                    onclick="editRole('${role.id}')">

                    Manage

                </button>

            </td>

        `;

        table.appendChild(row);

    });

}

function editRole(id){

    window.location.href=

        `/admin/roles/${id}`;

}

/* ==========================================================
   SYSTEM STATISTICS
   ========================================================== */

function updateAdminStatistics(){

    const stats = AdminDashboard.statistics;

    byId("totalUsers")?.textContent =

        stats.users || 0;

    byId("totalCourses")?.textContent =

        stats.courses || 0;

    byId("totalTeachers")?.textContent =

        stats.teachers || 0;

    byId("totalStudents")?.textContent =

        stats.students || 0;

    byId("activeUsers")?.textContent =

        stats.active || 0;

}

/* ==========================================================
   SYSTEM BACKUP
   ========================================================== */

async function backupDatabase(){

    try{

        const response = await fetch(

            "/api/admin/backup",

            {

                method:"POST"

            }

        );

        if(response.ok){

            showToast(

                "Backup Created",

                "Database backup completed successfully.",

                "success"

            );

        }

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   REFRESH ADMIN DASHBOARD
   ========================================================== */

function refreshAdminDashboard(){

    loadAdminDashboard();

    showToast(

        "Dashboard Updated",

        "Admin dashboard refreshed.",

        "success"

    );

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        loadAdminDashboard();

    }

);
/* ==========================================================
   PART 8
   ANALYTICS • CHARTS • EXPORTS • DATE FILTERS
   ========================================================== */

"use strict";

/* ==========================================================
   ANALYTICS
   ========================================================== */

const Analytics = {

    charts:{},

    filters:{

        from:null,

        to:null

    }

};

/* ==========================================================
   LOAD ANALYTICS
   ========================================================== */

async function loadAnalytics(){

    try{

        const response = await fetch(

            "/api/dashboard/analytics"

        );

        if(!response.ok) return;

        const data = await response.json();

        renderSubmissionTrend(data.submissions);

        renderLanguageChart(data.languages);

        renderScoreChart(data.scores);

        renderDailyActivity(data.activity);

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   SUBMISSION TREND
   ========================================================== */

function renderSubmissionTrend(data){

    const canvas = byId("submissionTrendChart");

    if(!canvas || typeof Chart==="undefined") return;

    if(Analytics.charts.trend){

        Analytics.charts.trend.destroy();

    }

    Analytics.charts.trend = new Chart(canvas,{

        type:"line",

        data:{

            labels:data.labels,

            datasets:[{

                label:"Submissions",

                data:data.values,

                borderColor:"#2563eb",

                backgroundColor:"rgba(37,99,235,.15)",

                fill:true,

                tension:.4

            }]

        },

        options:{

            responsive:true,

            maintainAspectRatio:false

        }

    });

}

/* ==========================================================
   LANGUAGE CHART
   ========================================================== */

function renderLanguageChart(data){

    const canvas = byId("languageUsageChart");

    if(!canvas || typeof Chart==="undefined") return;

    if(Analytics.charts.language){

        Analytics.charts.language.destroy();

    }

    Analytics.charts.language = new Chart(canvas,{

        type:"pie",

        data:{

            labels:data.labels,

            datasets:[{

                data:data.values,

                backgroundColor:[

                    "#2563eb",

                    "#16a34a",

                    "#dc2626",

                    "#f59e0b",

                    "#8b5cf6"

                ]

            }]

        }

    });

}

/* ==========================================================
   SCORE DISTRIBUTION
   ========================================================== */

function renderScoreChart(data){

    const canvas = byId("scoreChart");

    if(!canvas || typeof Chart==="undefined") return;

    if(Analytics.charts.score){

        Analytics.charts.score.destroy();

    }

    Analytics.charts.score = new Chart(canvas,{

        type:"bar",

        data:{

            labels:data.labels,

            datasets:[{

                label:"Students",

                data:data.values,

                backgroundColor:"#16a34a"

            }]

        },

        options:{

            responsive:true,

            maintainAspectRatio:false

        }

    });

}

/* ==========================================================
   DAILY ACTIVITY
   ========================================================== */

function renderDailyActivity(data){

    const table = byId("dailyActivityTable");

    if(!table) return;

    table.innerHTML="";

    data.forEach(item=>{

        const row=document.createElement("tr");

        row.innerHTML=`

            <td>${item.date}</td>

            <td>${item.logins}</td>

            <td>${item.submissions}</td>

            <td>${item.executions}</td>

        `;

        table.appendChild(row);

    });

}

/* ==========================================================
   DATE FILTER
   ========================================================== */

function applyAnalyticsFilter(){

    Analytics.filters.from =

        byId("fromDate")?.value;

    Analytics.filters.to =

        byId("toDate")?.value;

    loadAnalytics();

}

/* ==========================================================
   EXPORT CSV
   ========================================================== */

async function exportAnalyticsCSV(){

    window.location.href=

        "/api/dashboard/export/csv";

}

/* ==========================================================
   EXPORT PDF
   ========================================================== */

async function exportAnalyticsPDF(){

    window.location.href=

        "/api/dashboard/export/pdf";

}

/* ==========================================================
   EXPORT EXCEL
   ========================================================== */

async function exportAnalyticsExcel(){

    window.location.href=

        "/api/dashboard/export/excel";

}

/* ==========================================================
   DOWNLOAD CHART
   ========================================================== */

function downloadChart(chartName,fileName){

    const chart = Analytics.charts[chartName];

    if(!chart) return;

    const link = document.createElement("a");

    link.download = fileName + ".png";

    link.href = chart.toBase64Image();

    link.click();

}

/* ==========================================================
   REFRESH ANALYTICS
   ========================================================== */

function refreshAnalytics(){

    loadAnalytics();

    showToast(

        "Analytics Updated",

        "Dashboard analytics refreshed.",

        "success"

    );

}

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        loadAnalytics();

        byId("applyFilter")

        ?.addEventListener(

            "click",

            applyAnalyticsFilter

        );

    }

);
/* ==========================================================
   PART 9
   RESPONSIVE • KEYBOARD SHORTCUTS • AUTO REFRESH
   LOCAL STORAGE • ACCESSIBILITY • PERFORMANCE
   ========================================================== */

"use strict";

/* ==========================================================
   RESPONSIVE DASHBOARD
   ========================================================== */

function handleResponsiveLayout(){

    const mobile = window.innerWidth < 992;

    if(mobile){

        dashboard.sidebar?.classList.add("collapsed");

    }else{

        if(load("dashboardSidebar") !== false){

            dashboard.sidebar?.classList.remove("collapsed");

        }

    }

}

window.addEventListener(

    "resize",

    debounce(handleResponsiveLayout,200)

);

/* ==========================================================
   KEYBOARD SHORTCUTS
   ========================================================== */

document.addEventListener("keydown",(event)=>{

    if(event.ctrlKey && event.key.toLowerCase()==="b"){

        event.preventDefault();

        toggleSidebar();

    }

    if(event.ctrlKey && event.key.toLowerCase()==="f"){

        event.preventDefault();

        dashboard.search?.focus();

    }

    if(event.ctrlKey && event.key.toLowerCase()==="r"){

        event.preventDefault();

        refreshDashboard();

    }

    if(event.key==="Escape"){

        document.activeElement.blur();

    }

});

/* ==========================================================
   AUTO REFRESH
   ========================================================== */

function enableAutoRefresh(minutes=5){

    disableAutoRefresh();

    Dashboard.refreshInterval = setInterval(()=>{

        refreshDashboard();

        loadAnalytics?.();

        loadNotifications?.();

    },minutes*60*1000);

}

function disableAutoRefresh(){

    if(Dashboard.refreshInterval){

        clearInterval(

            Dashboard.refreshInterval

        );

    }

}

/* ==========================================================
   LOCAL STORAGE
   ========================================================== */

function saveDashboardPreference(key,value){

    save(

        "dashboard_"+key,

        value

    );

}

function loadDashboardPreference(key){

    return load(

        "dashboard_"+key

    );

}

/* ==========================================================
   COLLAPSED MENU STATE
   ========================================================== */

function saveSidebarState(){

    saveDashboardPreference(

        "sidebar",

        Dashboard.sidebarOpen

    );

}

function restoreSidebarState(){

    const state = loadDashboardPreference(

        "sidebar"

    );

    if(state===false){

        dashboard.sidebar?.classList.add(

            "collapsed"

        );

    }

}

/* ==========================================================
   ACCESSIBILITY
   ========================================================== */

function focusSearch(){

    dashboard.search?.focus();

}

function announce(message){

    let region = byId("liveRegion");

    if(!region){

        region = document.createElement("div");

        region.id = "liveRegion";

        region.setAttribute(

            "aria-live",

            "polite"

        );

        region.className = "visually-hidden";

        document.body.appendChild(region);

    }

    region.textContent = message;

}

/* ==========================================================
   SCROLL TO TOP
   ========================================================== */

function scrollToTop(){

    window.scrollTo({

        top:0,

        behavior:"smooth"

    });

}

window.addEventListener("scroll",()=>{

    const button = byId("scrollTop");

    if(!button) return;

    button.style.display =

        window.scrollY > 300

        ? "block"

        : "none";

});

/* ==========================================================
   PERFORMANCE
   ========================================================== */

function lazyLoadImages(){

    const images = document.querySelectorAll(

        "img[data-src]"

    );

    const observer = new IntersectionObserver(entries=>{

        entries.forEach(entry=>{

            if(entry.isIntersecting){

                const img = entry.target;

                img.src = img.dataset.src;

                img.removeAttribute("data-src");

                observer.unobserve(img);

            }

        });

    });

    images.forEach(img=>{

        observer.observe(img);

    });

}

/* ==========================================================
   COPY DASHBOARD LINK
   ========================================================== */

async function copyDashboardLink(){

    try{

        await navigator.clipboard.writeText(

            window.location.href

        );

        showToast(

            "Copied",

            "Dashboard link copied.",

            "success"

        );

    }

    catch(error){

        console.error(error);

    }

}

/* ==========================================================
   FULLSCREEN
   ========================================================== */

function toggleFullscreen(){

    if(!document.fullscreenElement){

        document.documentElement.requestFullscreen();

    }else{

        document.exitFullscreen();

    }

}

/* ==========================================================
   PAGE VISIBILITY
   ========================================================== */

document.addEventListener(

    "visibilitychange",

    ()=>{

        if(document.hidden){

            disableAutoRefresh();

        }else{

            enableAutoRefresh();

        }

    }

);

/* ==========================================================
   CONNECTION
   ========================================================== */

window.addEventListener("online",()=>{

    announce("Connection restored");

    showToast(

        "Online",

        "Connection restored.",

        "success"

    );

});

window.addEventListener("offline",()=>{

    announce("Connection lost");

    showToast(

        "Offline",

        "Internet connection lost.",

        "warning"

    );

});

/* ==========================================================
   INITIALIZATION
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    ()=>{

        handleResponsiveLayout();

        restoreSidebarState();

        lazyLoadImages();

        enableAutoRefresh();

    }

);
/* ==========================================================
   PART 10
   API WRAPPER • ERROR HANDLING • BOOTSTRAP
   SESSION • UTILITIES • FINAL INITIALIZATION
   ========================================================== */

"use strict";

/* ==========================================================
   VERSION
   ========================================================== */

const DASHBOARD_VERSION = "1.0.0";

/* ==========================================================
   API WRAPPER
   ========================================================== */

async function apiRequest(url, options = {}) {

    const config = {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        },
        ...options
    };

    try {

        const response = await fetch(url, config);

        if (response.status === 401) {

            showToast(
                "Session Expired",
                "Please login again.",
                "warning"
            );

            setTimeout(() => {

                window.location.href = "/login";

            }, 1000);

            return null;

        }

        return response;

    } catch (error) {

        console.error(error);

        showToast(
            "Network Error",
            "Unable to connect to server.",
            "danger"
        );

        return null;

    }

}

/* ==========================================================
   GLOBAL ERROR HANDLER
   ========================================================== */

window.addEventListener("error", event => {

    console.error(
        "Dashboard Error:",
        event.error
    );

});

window.addEventListener(

    "unhandledrejection",

    event => {

        console.error(
            "Unhandled Promise:",
            event.reason
        );

    }

);

/* ==========================================================
   BOOTSTRAP COMPONENTS
   ========================================================== */

function initializeBootstrapComponents() {

    if (typeof bootstrap === "undefined") {

        return;

    }

    document
        .querySelectorAll('[data-bs-toggle="tooltip"]')
        .forEach(el => {

            new bootstrap.Tooltip(el);

        });

    document
        .querySelectorAll('[data-bs-toggle="popover"]')
        .forEach(el => {

            new bootstrap.Popover(el);

        });

}

/* ==========================================================
   SESSION KEEP ALIVE
   ========================================================== */

function keepSessionAlive() {

    setInterval(async () => {

        try {

            await fetch("/api/session/ping");

        } catch (error) {

            console.warn("Ping failed.");

        }

    }, 5 * 60 * 1000);

}

/* ==========================================================
   LOADING OVERLAY
   ========================================================== */

function showLoading() {

    byId("loadingOverlay")
        ?.classList.remove("d-none");

}

function hideLoading() {

    byId("loadingOverlay")
        ?.classList.add("d-none");

}

/* ==========================================================
   SCROLL HELPERS
   ========================================================== */

function scrollToElement(id) {

    const element = byId(id);

    if (!element) return;

    element.scrollIntoView({

        behavior: "smooth",

        block: "center"

    });

}

/* ==========================================================
   DATE FORMAT
   ========================================================== */

function formatDate(date) {

    return new Date(date)
        .toLocaleDateString();

}

function formatDateTime(date) {

    return new Date(date)
        .toLocaleString();

}

/* ==========================================================
   FILE DOWNLOAD
   ========================================================== */

function downloadFile(url, filename) {

    const link =
        document.createElement("a");

    link.href = url;

    link.download = filename;

    document.body.appendChild(link);

    link.click();

    link.remove();

}

/* ==========================================================
   LOGGING
   ========================================================== */

function log(message) {

    console.log(
        `[Dashboard] ${message}`
    );

}

/* ==========================================================
   SYSTEM INFO
   ========================================================== */

function printVersion() {

    console.log(

        `%cLab Auto Grader Dashboard v${DASHBOARD_VERSION}`,

        "color:#2563eb;font-size:14px;font-weight:bold;"

    );

}

/* ==========================================================
   PAGE INITIALIZATION
   ========================================================== */

function initializeDashboardApplication() {

    initializeBootstrapComponents();

    handleResponsiveLayout();

    restoreTheme();

    restoreSidebarState();

    lazyLoadImages();

    keepSessionAlive();

    printVersion();

    log("Dashboard initialized.");

}

/* ==========================================================
   DOM READY
   ========================================================== */

document.addEventListener(

    "DOMContentLoaded",

    () => {

        initializeDashboardApplication();

    }

);

/* ==========================================================
   GLOBAL EXPORTS
   ========================================================== */

window.DashboardApp = {

    apiRequest,

    showToast,

    showLoading,

    hideLoading,

    toggleSidebar,

    toggleTheme,

    refreshDashboard,

    refreshStudentDashboard,

    refreshTeacherDashboard,

    refreshAdminDashboard,

    loadAnalytics,

    copyDashboardLink,

    toggleFullscreen,

    downloadFile,

    scrollToTop,

    scrollToElement,

    formatDate,

    formatDateTime

};

/* ==========================================================
   END OF DASHBOARD.JS
   ========================================================== */