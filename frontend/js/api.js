// Base URL and API Key
const BASE_URL = "http://127.0.0.1:8000"
const API_KEY = "mysecretkey123"

// Common headers
function getHeaders() {
    const token = localStorage.getItem("token")
    return {
        "x-api-key": API_KEY,
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    }
}

// AUTH 

// Signup
async function signup(username, email, password, role) {
    const response = await fetch(`${BASE_URL}/signup`, {
        method: "POST",
        headers: {
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, email, password, role })
    })
    return await response.json()
}

// Login
async function login(username, password) {
    const response = await fetch(`${BASE_URL}/login`, {
        method: "POST",
        headers: {
            "x-api-key": API_KEY,
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `username=${username}&password=${password}`
    })
    const data = await response.json()
    
    // save token
    if (data.access_token) {
        localStorage.setItem("token", data.access_token)
    }
    return data
}

// Logout
function logout() {
    localStorage.removeItem("token")
    window.location.href = "index.html"
}

// check login
function isLoggedIn() {
    return localStorage.getItem("token") !== null
}

// PAPERS 

// fetch all papers
async function fetchPapers() {
    const response = await fetch(`${BASE_URL}/papers`, {
        method: "GET",
        headers: getHeaders()
    })
    return await response.json()
}

// fetch single paper
async function fetchPaper(paper_id) {
    const response = await fetch(`${BASE_URL}/papers/${paper_id}`, {
        method: "GET",
        headers: getHeaders()
    })
    return await response.json()
}

// add paper
async function addPaper(paperData) {
    const response = await fetch(`${BASE_URL}/papers`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify(paperData)
    })
    return await response.json()
}

// update paper
async function updatePaper(paper_id, paperData) {
    const response = await fetch(`${BASE_URL}/papers/${paper_id}`, {
        method: "PUT",
        headers: getHeaders(),
        body: JSON.stringify(paperData)
    })
    return await response.json()
}

// delete paper
async function deletePaper(paper_id) {
    const response = await fetch(`${BASE_URL}/papers/${paper_id}`, {
        method: "DELETE",
        headers: getHeaders()
    })
    return await response.json()
}

// REPORTS 

// fetch all reports
async function fetchReports() {
    const response = await fetch(`${BASE_URL}/reports`, {
        method: "GET",
        headers: getHeaders()
    })
    return await response.json()
}

// fetch single paper
async function fetchReport(report_id) {
    const response = await fetch(`${BASE_URL}/reports/${report_id}`, {
        method: "GET",
        headers: getHeaders()
    })
    return await response.json()
}

// add report
async function addReport(reportData) {
    const response = await fetch(`${BASE_URL}/reports`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify(reportData)
    })
    return await response.json()
}

// update report
async function updateReport(report_id, reportData) {
    const response = await fetch(`${BASE_URL}/reports/${report_id}`, {
        method: "PUT",
        headers: getHeaders(),
        body: JSON.stringify(reportData)
    })
    return await response.json()
}

// delete report
async function deleteReport(report_id) {
    const response = await fetch(`${BASE_URL}/reports/${report_id}`, {
        method: "DELETE",
        headers: getHeaders()
    })
    return await response.json()
}