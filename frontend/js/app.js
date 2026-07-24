// =====================================================
// CrimeVision AI — Tamil Nadu State-Wide App Logic
// =====================================================

// Chart.js Config
Chart.defaults.color = '#94A3B8';
Chart.defaults.font.family = "'Inter',sans-serif";
Chart.defaults.font.size = 12;
const gridColor = 'rgba(255,255,255,0.05)';
const teal='#00E5FF', amber='#F59E0B', red='#F43F5E', green='#10B981', textDim='#94A3B8', purple='#8B5CF6';

// Global Chart Instances
let trendChart, sevChart, topCrimeChart, yoyChart, seasonChart, forecastChart, festivalChart;
let map, geojsonLayer;

// ===== STATE MANAGEMENT =====
let currentFilters = {
    state: 'Tamil Nadu',
    district: '',
    city: '',
    area: '',
    days: 30
};
let allDistricts = []; // cached list

// ===== UTILITY =====
function buildQueryString() {
    const params = new URLSearchParams();
    if (currentFilters.district) params.append('district', currentFilters.district);
    if (currentFilters.city) params.append('city', currentFilters.city);
    if (currentFilters.area) params.append('area', currentFilters.area);
    const qs = params.toString();
    return qs ? '?' + qs : '';
}

function getLocationLabel() {
    if (currentFilters.area) return `${currentFilters.area}, ${currentFilters.city || currentFilters.district}`;
    if (currentFilters.city) return `${currentFilters.city}, ${currentFilters.district}`;
    if (currentFilters.district) return `${currentFilters.district} District`;
    return 'Tamil Nadu (All Districts)';
}

function updateBranding() {
    const brandSub = document.getElementById('brandSub');
    const dashTitle = document.getElementById('dashboardTitle');
    const dashDesc = document.getElementById('dashboardDesc');
    const trendSub = document.getElementById('trendSub');
    const wantedSub = document.getElementById('wantedSub');
    const missingSub = document.getElementById('missingSub');
    
    if (currentFilters.district) {
        brandSub.textContent = `${currentFilters.district} District Command`;
        dashTitle.textContent = `${currentFilters.district} Command Dashboard`;
        dashDesc.textContent = `Crime posture for ${getLocationLabel()}`;
        trendSub.textContent = `All categories — ${getLocationLabel()}`;
        wantedSub.textContent = `High & Critical risk — ${currentFilters.district}`;
        missingSub.textContent = `Recent reports — ${currentFilters.district}`;
    } else {
        brandSub.textContent = 'Tamil Nadu State Command';
        dashTitle.textContent = 'State Command Dashboard';
        dashDesc.textContent = 'Tamil Nadu state-wide crime posture at a glance';
        trendSub.textContent = 'All categories, state-wide';
        wantedSub.textContent = 'High & Critical risk — state-wide';
        missingSub.textContent = 'Recent reports — state-wide';
    }
}

// ===== DETAIL MODAL =====
window.showDetailModal = function(title, subtitle, content) {
    document.getElementById('detailModalTitle').innerText = title;
    document.getElementById('detailModalSubtitle').innerText = subtitle;
    document.getElementById('detailModalBody').innerHTML = content;
    document.getElementById('detailModal').style.display = 'flex';
};
window.escapeForHtml = function(str) {
    if (!str) return '';
    return str.replace(/'/g, "\\'").replace(/"/g, '&quot;').replace(/\n/g, '<br>');
};

// ===== NAV SWITCHING =====
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        document.getElementById('view-' + item.dataset.view).classList.add('active');
        
        if (item.dataset.view === 'heatmap') {
            setTimeout(() => map && map.invalidateSize(), 100);
        }
    });
});

// ===== APP INITIALIZATION =====
async function initApp() {
    try {
        let user;
        try {
            user = await apiFetch("/users/me");
            document.getElementById('userAvatar').innerText = user.full_name.substring(0, 2).toUpperCase();
        } catch(e) {
            console.warn("User fetch failed, defaulting avatar", e);
            document.getElementById('userAvatar').innerText = "AD";
        }
        
        await loadLegalCategories();
        await loadDistricts();
        await refreshAllData();
        
        initCharts();
        initMap();
        setupFilterListeners();
        
    } catch (err) {
        console.error("Initialization error", err);
    }
}

// ===== DISTRICT LOADING =====
async function loadDistricts() {
    try {
        allDistricts = await apiFetch("/dashboard/districts");
    } catch(e) {
        allDistricts = [];
    }
    
    // Populate filter dropdown
    const filterDD = document.getElementById('filterDistrict');
    filterDD.innerHTML = '<option value="">All Districts</option>';
    allDistricts.forEach(d => {
        filterDD.innerHTML += `<option value="${d.name}">${d.name}</option>`;
    });
    
    // Populate FIR modal dropdown
    const firDD = document.getElementById('firDistrict');
    firDD.innerHTML = '<option value="">-- Select District --</option>';
    allDistricts.forEach(d => {
        firDD.innerHTML += `<option value="${d.name}">${d.name}</option>`;
    });
}

// ===== HIERARCHICAL FILTER LISTENERS =====
function setupFilterListeners() {
    const distFilter = document.getElementById('filterDistrict');
    const cityFilter = document.getElementById('filterCity');
    const areaFilter = document.getElementById('filterArea');
    const resetBtn = document.getElementById('resetFiltersBtn');
    
    distFilter.addEventListener('change', async (e) => {
        currentFilters.district = e.target.value;
        currentFilters.city = '';
        currentFilters.area = '';
        
        cityFilter.innerHTML = '<option value="">All Cities</option>';
        areaFilter.innerHTML = '<option value="">All Areas</option>';
        cityFilter.disabled = true;
        areaFilter.disabled = true;
        
        if (currentFilters.district) {
            resetBtn.style.display = 'inline-block';
            try {
                const cities = await apiFetch(`/dashboard/cities?district=${currentFilters.district}`);
                cities.forEach(c => { cityFilter.innerHTML += `<option value="${c}">${c}</option>`; });
                cityFilter.disabled = false;
            } catch(e) {}
        } else {
            resetBtn.style.display = 'none';
        }
        
        updateBranding();
        await refreshAllData();
    });
    
    cityFilter.addEventListener('change', async (e) => {
        currentFilters.city = e.target.value;
        currentFilters.area = '';
        areaFilter.innerHTML = '<option value="">All Areas</option>';
        areaFilter.disabled = true;
        
        if (currentFilters.city) {
            try {
                const areas = await apiFetch(`/dashboard/areas?district=${currentFilters.district}&city=${currentFilters.city}`);
                areas.forEach(a => { areaFilter.innerHTML += `<option value="${a}">${a}</option>`; });
                areaFilter.disabled = false;
            } catch(e) {}
        }
        
        updateBranding();
        await refreshAllData();
    });
    
    areaFilter.addEventListener('change', async (e) => {
        currentFilters.area = e.target.value;
        updateBranding();
        await refreshAllData();
    });
    
    resetBtn.addEventListener('click', () => {
        currentFilters.district = '';
        currentFilters.city = '';
        currentFilters.area = '';
        distFilter.value = '';
        cityFilter.innerHTML = '<option value="">All Cities</option>';
        areaFilter.innerHTML = '<option value="">All Areas</option>';
        cityFilter.disabled = true;
        areaFilter.disabled = true;
        resetBtn.style.display = 'none';
        updateBranding();
        refreshAllData();
        
        // Reset map zoom
        if (map) map.setView([11.1271, 78.6569], 7);
    });
    
    // FIR modal cascading
    document.getElementById('firDistrict').addEventListener('change', async (e) => {
        const firCity = document.getElementById('firCity');
        const firArea = document.getElementById('firArea');
        firCity.innerHTML = '<option value="">-- Select City --</option>';
        firArea.innerHTML = '<option value="">-- Select Area --</option>';
        if (e.target.value) {
            try {
                const cities = await apiFetch(`/dashboard/cities?district=${e.target.value}`);
                cities.forEach(c => { firCity.innerHTML += `<option value="${c}">${c}</option>`; });
            } catch(err) {}
        }
    });
    
    document.getElementById('firCity').addEventListener('change', async (e) => {
        const firArea = document.getElementById('firArea');
        firArea.innerHTML = '<option value="">-- Select Area --</option>';
        const dist = document.getElementById('firDistrict').value;
        if (e.target.value && dist) {
            try {
                const areas = await apiFetch(`/dashboard/areas?district=${dist}&city=${e.target.value}`);
                areas.forEach(a => { firArea.innerHTML += `<option value="${a}">${a}</option>`; });
            } catch(err) {}
        }
    });

    // Date Range Chips
    document.querySelectorAll('#view-dashboard .chip').forEach(chip => {
        chip.addEventListener('click', async (e) => {
            document.querySelectorAll('#view-dashboard .chip').forEach(c => c.classList.remove('active'));
            e.target.classList.add('active');
            currentFilters.days = parseInt(e.target.dataset.days) || 30;
            await loadCrimeTrend(); // Only refresh trend chart for now
        });
    });
}

// ===== DRILL DOWN HELPER =====
function drillToDistrict(distName) {
    currentFilters.district = distName;
    currentFilters.city = '';
    currentFilters.area = '';
    document.getElementById('filterDistrict').value = distName;
    document.getElementById('resetFiltersBtn').style.display = 'inline-block';
    updateBranding();
    refreshAllData();
    // Also load cities for the filter
    document.getElementById('filterDistrict').dispatchEvent(new Event('change'));
}

// ===== REFRESH ALL DATA =====
async function refreshAllData() {
    await Promise.all([
        loadDashboardStats(),
        loadAlerts(),
        loadLegalData(),
        loadForecast(),
        loadCrimeByType(),
        loadDistrictSummary(),
        loadMostWanted(),
        loadMissingPersons(),
        loadCrimeTrend(),
        loadRiskRanking(),
        loadCriminals(),
        loadMapMarkers(),
        loadYoYAnalytics(),
        loadSeasonalAnalytics(),
        loadFestivalImpact()
    ]);
}

// ===== ANALYTICS LOADERS =====
async function loadYoYAnalytics() {
    try {
        const data = await apiFetch("/dashboard/analytics/yoy" + buildQueryString());
        if (yoyChart && data) {
            yoyChart.data.datasets[0].data = data['2024'] || [0,0,0,0,0,0,0,0,0,0,0,0];
            yoyChart.data.datasets[1].data = data['2025'] || [0,0,0,0,0,0,0,0,0,0,0,0];
            yoyChart.data.datasets[2].data = data['2026'] || [0,0,0,0,0,0,0,0,0,0,0,0];
            yoyChart.update();
        }
    } catch(e) { console.error("YoY load error:", e); }
}

async function loadSeasonalAnalytics() {
    try {
        const data = await apiFetch("/dashboard/analytics/seasonal" + buildQueryString());
        if (seasonChart && data) {
            seasonChart.data.datasets[0].data = data;
            seasonChart.update();
        }
    } catch(e) { console.error("Seasonal load error:", e); }
}

async function loadFestivalImpact() {
    try {
        let url = "/dashboard/festival-impact";
        if (currentFilters.district) url += `?district=${encodeURIComponent(currentFilters.district)}`;
        const data = await apiFetch(url);
        if (festivalChart && data && data.length > 0) {
            festivalChart.data.labels = data.map(d => d.festival);
            festivalChart.data.datasets[0].data = data.map(d => d.uplift);
            festivalChart.update();
        }
    } catch(e) { console.error("Festival impact load error:", e); }
}

// ===== DATA LOADERS =====
async function loadDashboardStats() {
    try {
        const stats = await apiFetch("/dashboard/stats" + buildQueryString());
        document.getElementById('stat-crimes').innerText = stats.total_crimes_ytd.toLocaleString();
        document.getElementById('stat-active').innerText = stats.active_cases.toLocaleString();
        document.getElementById('stat-response').innerHTML = `${stats.avg_response_time_min}<span style="font-size:16px;color:var(--text-faint);"> min</span>`;
        document.getElementById('stat-disposal').innerHTML = `${stats.disposal_rate_pct}<span style="font-size:16px;color:var(--text-faint);">%</span>`;
    } catch(e) { console.error("Stats load error:", e); }
}

async function loadAlerts() {
    try {
        const alerts = await apiFetch("/dashboard/alerts" + buildQueryString());
        const container = document.getElementById('alertsContainer');
        const fullContainer = document.getElementById('alertsFullContainer');
        
        // Update badge
        document.getElementById('alertBadge').textContent = alerts.length;
        
        if (container) {
            container.innerHTML = '';
            if (alerts.length === 0) {
                container.innerHTML = '<p style="color:var(--text-dim); font-size:13px;">No recent alerts.</p>';
            }
            alerts.slice(0, 5).forEach(a => {
                let dotClass = 'sev-medium';
                if (a.severity === 'critical') dotClass = 'sev-critical';
                if (a.severity === 'high') dotClass = 'sev-high';
                
                const title = "Priority Alert Details";
                const sub = `${a.severity.toUpperCase()} · ${a.district || 'State'}`;
                const body = `<strong>Message:</strong> ${escapeForHtml(a.message)}<br><br><strong>Reported:</strong> ${new Date(a.created_at).toLocaleString()}`;
                
                container.innerHTML += `
                <div class="alert-item" style="cursor:pointer;" onclick="showDetailModal('${title}', '${sub}', '${body}')">
                    <span class="sev-dot ${dotClass}"></span>
                    <div style="flex:1;">
                        <div class="alert-text">${a.message}</div>
                        <div class="alert-meta">${a.severity.toUpperCase()} · ${a.district || 'State'} · ${new Date(a.created_at).toLocaleString()}</div>
                    </div>
                    <button class="btn" style="align-self:center;" onclick="event.stopPropagation();" data-i18n="btn_ack">Acknowledge</button>
                </div>`;
            });
        }
        
        if (fullContainer) {
            fullContainer.innerHTML = '';
            if (alerts.length === 0) {
                fullContainer.innerHTML = '<p style="color:var(--text-dim); font-size:13px;">No recent alerts for the selected location.</p>';
            }
            alerts.forEach(a => {
                let dotClass = 'sev-medium';
                if (a.severity === 'critical') dotClass = 'sev-critical';
                if (a.severity === 'high') dotClass = 'sev-high';
                
                const title = "Priority Alert Details";
                const sub = `${a.severity.toUpperCase()} · ${a.district || 'State'}`;
                const body = `<strong>Message:</strong> ${escapeForHtml(a.message)}<br><br><strong>Reported:</strong> ${new Date(a.created_at).toLocaleString()}`;
                
                fullContainer.innerHTML += `
                <div class="alert-item" style="cursor:pointer;" onclick="showDetailModal('${title}', '${sub}', '${body}')">
                    <span class="sev-dot ${dotClass}"></span>
                    <div style="flex:1;">
                        <div class="alert-text">${a.message}</div>
                        <div class="alert-meta">${a.severity.toUpperCase()} · ${a.district || 'State'} · ${a.city || ''} · ${new Date(a.created_at).toLocaleString()}</div>
                    </div>
                    <button class="btn" style="align-self:center;" onclick="event.stopPropagation();">Acknowledge</button>
                </div>`;
            });
        }
    } catch(e) { console.error("Alerts load error:", e); }
}

async function loadDeployments() {
    try {
        const deps = await apiFetch("/dashboard/deployments" + buildQueryString());
        const container = document.getElementById('deploymentsContainer');
        if (!container) return;
        container.innerHTML = '';
        if (deps.length === 0) {
            container.innerHTML = '<p style="color: var(--text-dim); font-size: 13px; grid-column: 1 / -1;">No pending deployments for the selected location.</p>';
            return;
        }
        deps.forEach(d => {
            let tagClass = 'tag-patrol';
            if (d.action_type.includes('CCTV')) tagClass = 'tag-cctv';
            if (d.action_type.includes('Emergency')) tagClass = 'tag-emergency';
            
            let color = 'var(--amber)';
            if (d.risk_score > 80) color = 'var(--red)';
            if (d.risk_score < 50) color = 'var(--green)';

            container.innerHTML += `
            <div class="deploy-card">
              <div class="deploy-top">
                <div>
                  <div class="deploy-loc">${d.location_name}</div>
                  <div style="font-size:11px; color:var(--text-dim); margin-top:2px;">${d.district}${d.city ? ' · ' + d.city : ''}</div>
                  <div class="deploy-tag ${tagClass}">${d.action_type}</div>
                </div>
                <div class="risk-score" style="color:${color};">${d.risk_score}</div>
              </div>
              <p style="font-size:12px; color:var(--text-dim); margin-top:10px;">${d.reason}</p>
              <div class="deploy-actions">
                <button class="btn btn-primary">Approve</button>
                <button class="btn">Reject</button>
              </div>
            </div>`;
        });
    } catch(e) { console.error("Deployments load error:", e); }
}

async function loadLegalData(query='', category='') {
    try {
        let url = `/legal/?query=${encodeURIComponent(query)}`;
        if (category) {
            url += `&category=${encodeURIComponent(category)}`;
        }
        const legal = await apiFetch(url);
        renderLegalTable(legal);
    } catch(e) { console.error("Legal load error:", e); }
}

function renderLegalTable(legal) {
    const tbody = document.getElementById('legalTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    legal.forEach(l => {
        const bailClass = l.is_bailable ? 'pill-resolved' : 'pill-open';
        const cogClass = l.is_cognizable ? 'pill-high' : 'pill-investigating';
        const compClass = l.is_compoundable ? 'pill-resolved' : 'pill-critical';
        
        tbody.innerHTML += `
        <tr>
            <td>${l.category || '-'}</td>
            <td style="font-weight:600; color:var(--text);">${l.crime_type}</td>
            <td class="mono" style="font-size:12px; color:var(--text-dim);">IPC: ${l.ipc_section}<br>BNS: <span style="color:var(--primary);">${l.bns_section}</span></td>
            <td style="font-size:13px;">${l.punishment}</td>
            <td>
                <div style="display:flex; flex-direction:column; gap:4px;">
                    <span class="pill ${bailClass}" style="font-size:10px;">${l.is_bailable ? 'Bailable' : 'Non-bailable'}</span>
                    <span class="pill ${cogClass}" style="font-size:10px;">${l.is_cognizable ? 'Cognizable' : 'Non-cognizable'}</span>
                </div>
            </td>
            <td>
                <button class="btn btn-primary" style="padding:6px 12px; font-size:12px;" onclick="showLegalDetails(${l.id})">View</button>
            </td>
        </tr>`;
    });
}

async function loadLegalCategories() {
    try {
        const categories = await apiFetch("/legal/categories");
        const select = document.getElementById('legalCategoryFilter');
        if (!select) return;
        select.innerHTML = '<option value="">All Categories</option>';
        categories.forEach(c => {
            select.innerHTML += `<option value="${c}">${c}</option>`;
        });
    } catch(e) { console.error("Legal categories load error:", e); }
}

async function showLegalDetails(id) {
    try {
        const data = await apiFetch(`/legal/${id}`);
        const modal = document.getElementById('legalModal');
        const content = document.getElementById('legalModalContent');
        
        const bailStr = data.is_bailable ? '<span style="color:var(--green)">Bailable</span>' : '<span style="color:var(--red)">Non-bailable</span>';
        const cogStr = data.is_cognizable ? '<span style="color:var(--red)">Cognizable</span>' : '<span style="color:var(--amber)">Non-cognizable</span>';
        const compStr = data.is_compoundable ? '<span style="color:var(--green)">Compoundable</span>' : '<span style="color:var(--red)">Non-compoundable</span>';

        content.innerHTML = `
            <div style="margin-bottom:20px;">
                <div class="eyebrow">${data.category || 'Legal Info'}</div>
                <h2 style="margin:5px 0;">${data.crime_type}</h2>
                <div style="display:flex; gap:10px; margin-top:10px;">
                    <div style="background:rgba(255,255,255,0.05); padding:8px 12px; border-radius:8px; border:1px solid var(--border);">
                        <span style="font-size:11px; color:var(--text-dim); display:block;">IPC SECTION</span>
                        <span class="mono" style="font-size:16px;">${data.ipc_section}</span>
                    </div>
                    <div style="background:rgba(100, 255, 218, 0.1); padding:8px 12px; border-radius:8px; border:1px solid var(--primary);">
                        <span style="font-size:11px; color:var(--primary); display:block;">BNS SECTION</span>
                        <span class="mono" style="font-size:16px; color:var(--primary);">${data.bns_section}</span>
                    </div>
                </div>
            </div>
            
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin-bottom:24px; padding-bottom:20px; border-bottom:1px solid var(--border);">
                <div><strong>Status:</strong><br>${bailStr}</div>
                <div><strong>Type:</strong><br>${cogStr}</div>
                <div><strong>Settlement:</strong><br>${compStr}</div>
            </div>
            
            <div style="margin-bottom:20px;">
                <h4 style="color:var(--text-dim); margin-bottom:8px;">Description</h4>
                <p style="font-size:14px; line-height:1.5;">${data.description || 'N/A'}</p>
            </div>
            
            <div style="margin-bottom:20px;">
                <h4 style="color:var(--text-dim); margin-bottom:8px;">Punishment</h4>
                <p style="font-size:14px; color:var(--red); font-weight:500;">${data.punishment}</p>
            </div>
            
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:20px;">
                <div>
                    <h4 style="color:var(--text-dim); margin-bottom:8px;">Investigation Procedure</h4>
                    <p style="font-size:13px;">${data.investigation_procedure || 'N/A'}</p>
                </div>
                <div>
                    <h4 style="color:var(--text-dim); margin-bottom:8px;">Evidence Required</h4>
                    <p style="font-size:13px;">${data.evidence_required || 'N/A'}</p>
                </div>
            </div>
            
            <div style="margin-bottom:20px;">
                <h4 style="color:var(--text-dim); margin-bottom:8px;">Court Jurisdiction</h4>
                <p style="font-size:13px;">${data.court_jurisdiction || 'N/A'}</p>
            </div>
            
            ${data.legal_notes ? `
            <div style="padding:12px; background:rgba(255, 171, 0, 0.1); border-left:3px solid var(--amber); border-radius:4px;">
                <h4 style="color:var(--amber); margin-bottom:4px; font-size:12px;">Legal Notes / Exceptions</h4>
                <p style="font-size:13px; margin:0;">${data.legal_notes}</p>
            </div>` : ''}
        `;
        modal.style.display = 'flex';
    } catch(e) { console.error("Legal details error:", e); }
}

async function loadForecast() {
    try {
        let url = "/ai/forecast";
        if (currentFilters.district) url += `?district=${currentFilters.district}`;
        const data = await apiFetch(url);
        if (forecastChart && data.length > 0) {
            forecastChart.data.labels = data.map(d => d.day);
            forecastChart.data.datasets[0].data = data.map(d => d.upper_bound);
            forecastChart.data.datasets[1].data = data.map(d => d.forecast);
            forecastChart.data.datasets[2].data = data.map(d => d.lower_bound);
            forecastChart.update();
        }
    } catch(e) { console.error("Forecast load error:", e); }
}

async function loadCrimeByType() {
    try {
        const data = await apiFetch("/dashboard/crime-by-type" + buildQueryString());
        
        // Update top crime bar chart
        if (topCrimeChart && data.length > 0) {
            const top5 = data.slice(0, 6);
            topCrimeChart.data.labels = top5.map(d => d.crime_type);
            topCrimeChart.data.datasets[0].data = top5.map(d => d.count);
            topCrimeChart.update();
        }
        
        // Update severity/type doughnut
        if (sevChart && data.length > 0) {
            sevChart.data.labels = data.map(d => d.crime_type);
            sevChart.data.datasets[0].data = data.map(d => d.count);
            // Generate colors
            const colors = [green, teal, amber, red, purple, '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'];
            sevChart.data.datasets[0].backgroundColor = colors.slice(0, data.length);
            sevChart.update();
        }
        
        // Update case status table
        const caseBody = document.getElementById('caseStatusBody');
        if (caseBody && data.length > 0) {
            caseBody.innerHTML = '';
            data.forEach(d => {
                const openCount = d.open_cases || 0;
                const invCount = d.investigating_cases || 0;
                const resCount = d.resolved_cases || 0;
                caseBody.innerHTML += `
                <tr>
                    <td>${d.crime_type}</td>
                    <td><span class="pill pill-open">${openCount}</span></td>
                    <td><span class="pill pill-progress">${invCount}</span></td>
                    <td><span class="pill pill-resolved">${resCount}</span></td>
                </tr>`;
            });
        }
    } catch(e) { console.error("Crime by type load error:", e); }
}

async function loadDistrictSummary() {
    try {
        const data = await apiFetch("/dashboard/district-summary");
        const tbody = document.getElementById('districtSummaryBody');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        // Sort by total descending
        data.sort((a, b) => b.total - a.total);
        
        data.forEach(d => {
            const disposal = d.total > 0 ? ((d.resolved / d.total) * 100).toFixed(1) : '0.0';
            const disposalColor = disposal > 40 ? 'var(--green)' : disposal > 25 ? 'var(--amber)' : 'var(--red)';
            tbody.innerHTML += `
            <tr>
                <td><span class="district-link" onclick="drillToDistrict('${d.district}')">${d.district}</span></td>
                <td class="mono">${d.total}</td>
                <td class="mono">${d.open_cases}</td>
                <td class="mono">${d.resolved}</td>
                <td style="color:${disposalColor}; font-weight:600; font-family:var(--font-mono);">${disposal}%</td>
                <td><button class="btn" style="font-size:11px; padding:6px 12px;" onclick="drillToDistrict('${d.district}')">View</button></td>
            </tr>`;
        });
    } catch(e) { console.error("District summary load error:", e); }
}

async function loadMostWanted() {
    try {
        let url = "/dashboard/most-wanted";
        if (currentFilters.district) url += `?district=${currentFilters.district}`;
        const data = await apiFetch(url);
        const container = document.getElementById('wantedContainer');
        if (!container) return;
        container.innerHTML = '';
        
        if (data.length === 0) {
            container.innerHTML = '<p style="color:var(--text-dim); font-size:13px;">No high-risk criminals found.</p>';
            return;
        }
        
        data.slice(0, 5).forEach(c => {
            const initials = c.name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
            const riskPill = c.risk_level === 'critical' 
                ? '<span class="pill pill-open">CRITICAL</span>' 
                : '<span class="pill pill-progress">HIGH</span>';
            const title = `Criminal Profile: ${escapeForHtml(c.name)}`;
            const sub = c.risk_level.toUpperCase() + " RISK";
            const body = `<strong>Name:</strong> ${escapeForHtml(c.name)}<br><strong>Alias:</strong> ${escapeForHtml(c.alias) || 'None'}<br><strong>Last Known Location:</strong> ${c.district || 'Unknown'} ${c.city ? ' - ' + c.city : ''}<br><br><strong>Crime History:</strong><br>${escapeForHtml(c.crime_history) || 'N/A'}`;
            
            container.innerHTML += `
            <div class="person-item" style="cursor:pointer;" onclick="showDetailModal('${title}', '${sub}', '${body}')">
                <div class="person-avatar wanted">${initials}</div>
                <div style="flex:1;">
                    <div class="person-name">${c.name} ${c.alias ? '(' + c.alias + ')' : ''}</div>
                    <div class="person-meta">${c.district || 'Unknown'} · ${c.city || ''} · ${riskPill}</div>
                </div>
            </div>`;
        });
    } catch(e) { console.error("Most wanted load error:", e); }
}

async function loadMissingPersons() {
    try {
        let url = "/dashboard/missing-persons";
        if (currentFilters.district) url += `?district=${currentFilters.district}`;
        const data = await apiFetch(url);
        const container = document.getElementById('missingContainer');
        if (!container) return;
        container.innerHTML = '';
        
        if (data.length === 0) {
            container.innerHTML = '<p style="color:var(--text-dim); font-size:13px;">No missing person reports found.</p>';
            return;
        }
        
        data.slice(0, 5).forEach(f => {
            const title = `Missing Person: ${f.fir_number}`;
            const sub = `Reported on ${new Date(f.date_reported).toLocaleDateString()}`;
            const body = `<strong>FIR Number:</strong> ${f.fir_number}<br><strong>Reported From:</strong> ${f.district} ${f.city ? '· ' + f.city : ''} ${f.area ? '· ' + f.area : ''}<br><strong>Status:</strong> ${f.status.toUpperCase()}<br><br><strong>Incident Description:</strong><br>${escapeForHtml(f.incident_description) || 'No details available.'}`;
            
            container.innerHTML += `
            <div class="person-item" style="cursor:pointer;" onclick="showDetailModal('${title}', '${sub}', '${body}')">
                <div class="person-avatar missing">MP</div>
                <div style="flex:1;">
                    <div class="person-name">${f.fir_number}</div>
                    <div class="person-meta">${f.district} · ${f.city || f.area || f.location_name} · ${new Date(f.date_reported).toLocaleDateString()}</div>
                </div>
                <span class="pill pill-${f.status === 'resolved' ? 'resolved' : f.status === 'investigating' ? 'progress' : 'open'}">${f.status}</span>
            </div>`;
        });
    } catch(e) { console.error("Missing persons load error:", e); }
}

async function loadCrimeTrend() {
    try {
        const data = await apiFetch("/dashboard/crime-trend" + buildQueryString() + (buildQueryString() ? '&' : '?') + 'days=' + currentFilters.days);
        if (trendChart && data.length > 0) {
            trendChart.data.labels = data.map(d => d.day.substring(5)); // MM-DD format
            trendChart.data.datasets[0].data = data.map(d => d.count);
            trendChart.update();
        }
    } catch(e) { console.error("Crime trend load error:", e); }
}

async function loadRiskRanking() {
    try {
        const data = await apiFetch("/dashboard/risk-ranking");
        const tbody = document.getElementById('riskRankingBody');
        if (!tbody) return;
        tbody.innerHTML = '';
        data.slice(0, 5).forEach((r, i) => {
            const riskColor = r.risk > 80 ? 'var(--red)' : r.risk > 50 ? 'var(--amber)' : 'var(--green)';
            tbody.innerHTML += `
            <tr>
                <td>#${i+1}</td>
                <td><span class="district-link" onclick="drillToDistrict('${r.district}')">${r.district}</span></td>
                <td>
                    <div style="width:100%; height:6px; background:var(--surface); border-radius:3px; overflow:hidden;">
                        <div style="width:${r.risk}%; height:100%; background:${riskColor};"></div>
                    </div>
                </td>
                <td class="mono">${r.risk}%</td>
            </tr>`;
        });
    } catch(e) { console.error("Risk ranking load error:", e); }
}

async function loadCriminals() {
    try {
        const data = await apiFetch("/criminals/" + buildQueryString());
        const tbody = document.getElementById('criminalsTableBody');
        if (!tbody) return;
        tbody.innerHTML = '';
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="color:var(--text-dim); text-align:center;">No records found.</td></tr>';
            return;
        }
        data.forEach(c => {
            const riskPill = c.risk_level === 'critical' ? '<span class="pill pill-open">CRITICAL</span>' : c.risk_level === 'high' ? '<span class="pill pill-progress">HIGH</span>' : `<span class="pill pill-resolved">${c.risk_level.toUpperCase()}</span>`;
            tbody.innerHTML += `
            <tr>
                <td>${c.name} ${c.alias ? '<br><small style="color:var(--text-dim);">'+c.alias+'</small>' : ''}</td>
                <td>${riskPill}</td>
                <td>${c.crime_history}</td>
                <td>${c.district} ${c.city ? '- ' + c.city : ''}</td>
                <td><button class="btn" onclick="alert('CRIMINAL PROFILE\\n\\nName: ${c.name}\\nAlias: ${c.alias || 'N/A'}\\nRisk Level: ${c.risk_level.toUpperCase()}\\nLocation: ${c.district} - ${c.city || 'N/A'}\\n\\nHistory: ${c.crime_history}\\n\\nStatus: Under active surveillance by ${c.district} district command.')">View</button></td>
            </tr>`;
        });
    } catch(e) { console.error("Criminals load error:", e); }
}

async function loadEmergencies() {
    try {
        const data = await apiFetch("/emergency/" + buildQueryString());
        const container = document.getElementById('emergencyContainer');
        if (!container) return;
        container.innerHTML = '';
        if (data.length === 0) {
            container.innerHTML = '<p style="color:var(--text-dim);font-size:13px;grid-column:1/-1;">No active emergencies.</p>';
            return;
        }
        data.forEach(e => {
            container.innerHTML += `
            <div class="card" style="border: 1px solid var(--red);">
                <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                    <div class="eyebrow" style="color:var(--red);">LIVE INCIDENT</div>
                    <span class="pill pill-open">${e.status}</span>
                </div>
                <h3 style="margin-bottom:5px; color:var(--text);">${e.incident_type}</h3>
                <p style="color:var(--text-dim); font-size:12px; margin-bottom:15px;">${e.description}</p>
                <div style="display:flex; gap:10px;">
                    <button class="btn btn-primary" style="flex:1;">Dispatch</button>
                    <button class="btn" style="flex:1;">Resolve</button>
                </div>
            </div>`;
        });
    } catch(e) { console.error("Emergencies load error:", e); }
}

function exportFIRs() {
    let url = "http://localhost:8000/firs/export";
    if (currentFilters.district) {
        url += `?district=${currentFilters.district}`;
    }
    fetch(url, { headers: { "Authorization": `Bearer ${jwtToken}` } })
        .then(res => res.blob())
        .then(blob => {
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `firs_${currentFilters.district || 'TN'}.csv`;
            a.click();
        });
}


// ===== CHART INITIALIZATIONS =====
function initCharts() {
    trendChart = new Chart(document.getElementById('trendChart'), {
        type:'line',
        data:{ labels:[],
          datasets:[{ data:[],
            borderColor:teal, backgroundColor:'rgba(46,180,196,.08)', fill:true, tension:.35, pointRadius:0, borderWidth:2 }]},
        options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{ x:{ grid:{color:gridColor}, ticks:{maxTicksLimit:8} }, y:{ grid:{color:gridColor} } } }
    });
    
    sevChart = new Chart(document.getElementById('sevChart'), {
        type:'doughnut',
        data:{ labels:[], datasets:[{ data:[], backgroundColor:[green,teal,amber,red,purple], borderWidth:0 }]},
        options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom', labels:{boxWidth:10, padding:14}}}, cutout:'62%' }
    });

    topCrimeChart = new Chart(document.getElementById('topCrimeChart'), {
        type:'bar',
        data:{ labels:[],
          datasets:[{ data:[], backgroundColor:teal, borderRadius:4, barThickness:22 }]},
        options:{ indexAxis:'y', responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{ x:{grid:{color:gridColor}}, y:{grid:{display:false}} } }
    });

    yoyChart = new Chart(document.getElementById('yoyChart'), {
        type:'line',
        data:{ labels:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
          datasets:[
            {label:'2024', data:[0,0,0,0,0,0,0,0,0,0,0,0], borderColor:textDim, borderDash:[4,3], pointRadius:0, borderWidth:1.5},
            {label:'2025', data:[0,0,0,0,0,0,0,0,0,0,0,0], borderColor:amber, pointRadius:0, borderWidth:2},
            {label:'2026', data:[0,0,0,0,0,0,0,0,0,0,0,0], borderColor:teal, pointRadius:2, borderWidth:2.5}
          ]},
        options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top', labels:{boxWidth:10}}}, scales:{ x:{grid:{color:gridColor}}, y:{grid:{color:gridColor}} } }
    });

    seasonChart = new Chart(document.getElementById('seasonChart'), {
        type:'bar',
        data:{ labels:['Q1','Q2','Q3','Q4'], datasets:[{ data:[0,0,0,0], backgroundColor:[teal,teal,amber,red], borderRadius:5 }]},
        options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{x:{grid:{display:false}}, y:{grid:{color:gridColor}}} }
    });

    forecastChart = new Chart(document.getElementById('forecastChart'), {
        type:'line',
        data:{ labels:[],
          datasets:[
            {label:'Upper 80%', data:[], borderColor:'rgba(46,180,196,0.3)', backgroundColor:'rgba(46,180,196,.12)', fill:'+1', pointRadius:0, borderWidth:1},
            {label:'Forecast', data:[], borderColor:teal, backgroundColor:'transparent', fill:false, pointRadius:0, borderWidth:2.5},
            {label:'Lower 80%', data:[], borderColor:'rgba(46,180,196,0.3)', backgroundColor:'transparent', fill:false, pointRadius:0, borderWidth:1}
          ]},
        options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top', labels:{boxWidth:10, filter:(item)=>item.datasetIndex===1}}}, scales:{x:{grid:{color:gridColor}, ticks:{maxTicksLimit:6}}, y:{grid:{color:gridColor}, beginAtZero:true}} }
    });

    festivalChart = new Chart(document.getElementById('festivalChart'), {
        type:'bar',
        data:{ labels:[], datasets:[{ data:[], backgroundColor:amber, borderRadius:5 }]},
        options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{x:{grid:{display:false}}, y:{grid:{color:gridColor}, beginAtZero:true, title:{display:true, text:'% uplift', color:textDim}}} }
    });
}

// ===== LEAFLET MAP INITIALIZATION =====
let markersLayer = L.layerGroup();

async function initMap() {
    map = L.map('map', {
        zoomControl: true,
        attributionControl: false
    }).setView([11.1271, 78.6569], 7); // Center of Tamil Nadu

    L.tileLayer('http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        attribution: 'Map data &copy; Google'
    }).addTo(map);
    
    markersLayer.addTo(map);

    // Map Reset button
    document.getElementById('mapResetBtn').addEventListener('click', () => {
        map.setView([11.1271, 78.6569], 7);
        if (geojsonLayer) geojsonLayer.resetStyle();
    });

    try {
        const response = await fetch('data/tn.geojson');
        const geojsonData = await response.json();
        
        // Compute crime counts per district for coloring
        let districtCrimeCounts = {};
        try {
            const summary = await apiFetch("/dashboard/district-summary");
            summary.forEach(s => { districtCrimeCounts[s.district] = s.total; });
        } catch(e) {}
        
        geojsonLayer = L.geoJSON(geojsonData, {
            style: function(feature) {
                const distName = feature.properties.NAME_2 || feature.properties.district || feature.properties.name || "Unknown";
                const count = districtCrimeCounts[distName] || 0;
                
                let color = '#49AD7C'; // Green (safe)
                if (count > 60) color = '#DD5449'; // Red (high)
                else if (count > 30) color = '#E3A23D'; // Amber (medium)
                
                return {
                    color: 'rgba(255,255,255,0.4)',
                    weight: 1.5,
                    fillColor: color,
                    fillOpacity: 0.15
                };
            },
            onEachFeature: function(feature, layer) {
                const distName = feature.properties.NAME_2 || feature.properties.district || feature.properties.name || "Unknown";
                const count = districtCrimeCounts[distName] || 0;
                
                layer.on('mouseover', function(e) {
                    this.setStyle({ fillOpacity: 0.4, weight: 2.5, color: '#00E5FF' });
                });
                layer.on('mouseout', function(e) {
                    geojsonLayer.resetStyle(e.target);
                });
                layer.on('click', function(e) {
                    // Drill down to district
                    drillToDistrict(distName);
                    
                    // Zoom into the district
                    map.fitBounds(e.target.getBounds(), { padding: [30, 30] });
                });
                layer.bindTooltip(`<b>${distName}</b><br>${count} FIRs`, { sticky: true });
            }
        }).addTo(map);
    } catch(err) {
        console.error("GeoJSON load failed:", err);
    }
}

async function loadMapMarkers() {
    if (!map) return;
    try {
        const markers = await apiFetch("/dashboard/map-markers" + buildQueryString());
        markersLayer.clearLayers();
        
        const redIcon = L.divIcon({
            className: 'custom-div-icon',
            html: "<div style='background-color:var(--red);width:8px;height:8px;border-radius:50%;box-shadow:0 0 8px var(--red); opacity:0.8;'></div>",
            iconSize: [8, 8],
            iconAnchor: [4, 4]
        });

        markers.forEach(m => {
            if(m.latitude && m.longitude) {
                const marker = L.marker([m.latitude, m.longitude], {icon: redIcon});
                marker.bindPopup(`<b>${m.crime_type}</b><br>${m.fir_number}<br>${new Date(m.date_reported).toLocaleDateString()}`);
                markersLayer.addLayer(marker);
            }
        });
    } catch(e) { console.error("Map markers load error", e); }
}



// ===== FIR SUBMISSION =====
document.getElementById('submitFirBtn').addEventListener('click', async () => {
    const district = document.getElementById('firDistrict').value;
    const city = document.getElementById('firCity').value;
    const area = document.getElementById('firArea').value;
    const crime_type = document.getElementById('firCrimeType').value;
    const police_station = document.getElementById('firPoliceStation').value;
    const location_name = document.getElementById('firLocation').value;
    const desc = document.getElementById('firDesc').value;
    
    if (!district || !desc) {
        alert("Please select a district and enter incident description.");
        return;
    }
    
    try {
        const response = await apiFetch("/firs/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                state: "Tamil Nadu",
                district: district,
                city: city || null,
                area: area || null,
                police_station: police_station || `${district} PS`,
                crime_type: crime_type,
                crime_category: "Misc",
                incident_description: desc,
                location_name: location_name || `${area || city || district}`
            })
        });
        
        alert(`FIR Successfully Registered!\nFIR Number: ${response.fir_number}\nDistrict: ${district}`);
        document.getElementById('firModal').style.display = 'none';
        
        // Reload dashboard
        refreshAllData();
    } catch(err) {
        alert("Failed to submit FIR.");
        console.error(err);
    }
});

// ===== LANGUAGE SWITCHER =====
document.getElementById('langSelect').addEventListener('change', (e) => {
    if (typeof changeLanguage === 'function') {
        changeLanguage(e.target.value);
    }
});

// ===== LOGIN =====
document.getElementById('loginBtn').addEventListener('click', async () => {
    const user = document.getElementById('usernameInput').value;
    const pass = document.getElementById('passwordInput').value;
    try {
        await login(user, pass);
        document.getElementById('loginModal').style.display = 'none';
        initApp();
    } catch(e) {
        alert("Invalid credentials");
    }
});

// ===== LEGAL SEARCH =====
const legalSearchInput = document.getElementById('legalSearch');
const legalCategoryFilter = document.getElementById('legalCategoryFilter');

function triggerLegalSearch() {
    const q = legalSearchInput ? legalSearchInput.value : '';
    const cat = legalCategoryFilter ? legalCategoryFilter.value : '';
    loadLegalData(q, cat);
}

if (legalSearchInput) {
    legalSearchInput.addEventListener('input', triggerLegalSearch);
}
if (legalCategoryFilter) {
    legalCategoryFilter.addEventListener('change', triggerLegalSearch);
}

// ===== BOOT =====
if (jwtToken) {
    initApp();
    // Real-time Simulation
    setInterval(() => {
        loadDashboardStats();
        loadAlerts();
    }, 60000); // refresh stats and alerts every 60 seconds
} else {
    document.getElementById('loginModal').style.display = 'flex';
}
