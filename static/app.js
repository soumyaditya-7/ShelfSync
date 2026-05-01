/**
 * ShelfSync – Next Gen Library Management - SPA Logic
 */

const app = {
    state: {
        books: [],
        students: [],
        issued: [],
        currentTab: 'dashboard',
        circulationTab: 'all',
        chartInstance: null,
        reportsTrendChart: null,
        reportsStatusChart: null
    },

    // UI Utilities
    ui: {
        showToast(message, type = 'success') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            const icon = type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation';
            toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
            
            container.appendChild(toast);
            setTimeout(() => {
                toast.classList.add('toast-closing');
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        },

        openModal(id) {
            const modal = document.getElementById(id);
            if (modal) {
                modal.classList.add('show');
                // Reset forms inside if any
                const form = modal.querySelector('form');
                if (form && id !== 'returnBookModal' && id !== 'editMemberModal') form.reset();
            }
        },

        closeModal(id) {
            const modal = id ? document.getElementById(id) : document.querySelector('.modal.show');
            if (modal) {
                modal.classList.remove('show');
                if(modal.id === 'returnBookModal'){
                    document.getElementById('return-fine-alert').classList.add('d-none');
                }
            }
        },

        toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('open');
        },

        renderSkeleton(columns) {
            let html = '';
            for(let i=0; i<3; i++) {
                html += `<tr>`;
                for(let j=0; j<columns; j++) {
                    html += `<td><div class="skeleton skeleton-row"></div></td>`;
                }
                html += `</tr>`;
            }
            return html;
        },

        initScrollAnimations() {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if(entry.isIntersecting) {
                        entry.target.classList.add('in-view');
                    }
                });
            }, { threshold: 0.1 });

            document.querySelectorAll('.scroll-anim:not(.in-view)').forEach(el => observer.observe(el));
        }
    },

    // Initialization
    async init() {
        this.setupEventListeners();
        await this.fetchAllData();
        this.renderDashboard();
    },

    setupEventListeners() {
        // Tab Navigation
        document.querySelectorAll('.nav-link').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                this.switchTab(tab);
            });
        });

        // Modals Close
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if(modal) this.ui.closeModal(modal.id);
            });
        });

        // Global Search
        document.getElementById('global-search').addEventListener('input', (e) => {
            const query = e.target.value;
            this.switchTab('books');
            document.getElementById('books-search-input').value = query;
            this.renderBooksTab(query);
        });

        // Table local filters
        document.getElementById('books-search-input').addEventListener('input', (e) => this.renderBooksTab(e.target.value));
        document.getElementById('members-search-input').addEventListener('input', (e) => this.renderMembersTab(e.target.value));

        // Circulation Sub-tabs
        document.querySelectorAll('#circulation-tabs .tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('#circulation-tabs .tab-btn').forEach(b => b.classList.remove('active'));
                const target = e.currentTarget;
                target.classList.add('active');
                this.state.circulationTab = target.dataset.filter;
                this.renderCirculationTab();
            });
        });

        // Forms 
        document.getElementById('addBookForm').addEventListener('submit', this.handlers.addBook);
        document.getElementById('addMemberForm').addEventListener('submit', this.handlers.addMember);
        document.getElementById('editMemberForm').addEventListener('submit', this.handlers.editMember);
        document.getElementById('issueBookForm').addEventListener('submit', this.handlers.issueBook);
        document.getElementById('adminSettingsForm').addEventListener('submit', this.handlers.saveAdminSettings);
    },

    // Navigation
    switchTab(tabId) {
        this.state.currentTab = tabId;
        
        // Update Nav Menu
        document.querySelectorAll('.nav-link').forEach(btn => btn.classList.remove('active'));
        const navBtn = document.querySelector(`.nav-link[data-tab="${tabId}"]`);
        if(navBtn) navBtn.classList.add('active');

        // Update Views
        document.querySelectorAll('.view-section').forEach(view => view.classList.remove('active'));
        const targetView = document.getElementById(`view-${tabId}`);
        if(targetView) targetView.classList.add('active');

        // Mobile close sidebar
        document.getElementById('sidebar').classList.remove('open');

        // Render context
        this.refreshCurrentTab();
    },

    refreshCurrentTab() {
        if(this.state.currentTab === 'dashboard') this.renderDashboard();
        else if(this.state.currentTab === 'books') this.renderBooksTab();
        else if(this.state.currentTab === 'members') this.renderMembersTab();
        else if(this.state.currentTab === 'circulation') this.renderCirculationTab();
        else if(this.state.currentTab === 'reports') this.renderReportsTab();
    },

    // Data Fetching
    async fetchAllData() {
        try {
            const [booksRes, studentsRes, issuedRes] = await Promise.all([
                fetch('/api/books'),
                fetch('/api/students'),
                fetch('/api/issued_books')
            ]);
            
            if(booksRes.ok) this.state.books = await booksRes.json();
            if(studentsRes.ok) this.state.students = await studentsRes.json();
            if(issuedRes.ok) this.state.issued = await issuedRes.json();
            
        } catch(e) {
            console.error("Failed to load data", e);
            this.ui.showToast("Failed to connect to the server", "error");
        }
    },

    // Rendering Logic
    renderDashboard() {
        let totalTitles = this.state.books.length;
        let totalCopies = 0;
        let availableCopies = 0;
        
        this.state.books.forEach(b => {
            totalCopies += b.total_copies;
            availableCopies += b.available_copies;
        });

        // Update Stats
        document.getElementById('dash-total-titles').textContent = totalTitles;
        document.getElementById('dash-total-copies').textContent = totalCopies;
        document.getElementById('dash-available-copies').textContent = availableCopies;
        document.getElementById('dash-active-issues').textContent = this.state.issued.length;

        // Render Chart
        this.renderChart(availableCopies, totalCopies - availableCopies);

        // Render Recent Activity
        const activityList = document.getElementById('dash-recent-activity');
        activityList.innerHTML = '';
        if(this.state.issued.length === 0) {
            activityList.innerHTML = '<p class="text-muted" style="padding:1rem;">No recent activities.</p>';
        } else {
            // grab last 4
            const recent = [...this.state.issued].reverse().slice(0, 4);
            recent.forEach(r => {
                activityList.innerHTML += `
                    <div class="activity-item">
                        <div class="activity-icon"><i class="fa-solid fa-bookmark"></i></div>
                        <div class="activity-info">
                            <h4>Issued: ${r.book_title}</h4>
                            <p>To ${r.student_name} (${r.student_id}) on ${r.issue_date || 'recently'}</p>
                        </div>
                    </div>
                `;
            });
        }
    },

    renderChart(available, issuedOut) {
        const ctx = document.getElementById('inventoryChart');
        if(!ctx) return;
        
        if(this.state.chartInstance) {
            this.state.chartInstance.destroy();
        }

        this.state.chartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Available', 'Issued Out'],
                datasets: [{
                    data: [available, issuedOut],
                    backgroundColor: ['#10B981', '#F59E0B'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                },
                cutout: '75%'
            }
        });
    },

    renderBooksTab(filterQuery = '') {
        const tbody = document.getElementById('books-list-tbody');
        const empty = document.getElementById('books-empty');
        const q = filterQuery.toLowerCase();
        
        const filtered = this.state.books.filter(b => 
            b.title.toLowerCase().includes(q) || 
            b.author.toLowerCase().includes(q) || 
            b.isbn.toLowerCase().includes(q)
        );

        document.getElementById('books-count-label').textContent = `${filtered.length} total records`;

        tbody.innerHTML = '';
        if(filtered.length === 0) {
            empty.classList.remove('d-none');
        } else {
            empty.classList.add('d-none');
            filtered.forEach(b => {
                let badge = 'badge-success';
                let label = 'Available';
                if(b.available_copies === 0) { badge = 'badge-danger'; label = 'Out of Stock'; }
                else if(b.available_copies <= 2) { badge = 'badge-warning'; label = 'Low Stock'; }

                const tr = document.createElement('tr');
                tr.className = 'scroll-anim';
                tr.innerHTML = `
                    <td>
                        <strong class="text-primary">${b.title}</strong>
                        <div class="text-muted" style="margin-top:2px"><i class="fa-solid fa-barcode"></i> ISBN: ${b.isbn}</div>
                    </td>
                    <td>${b.author}</td>
                    <td>${b.isbn}</td>
                    <td><strong>${b.available_copies}</strong> / ${b.total_copies}</td>
                    <td><span class="badge ${badge}">${label}</span></td>
                    <td>
                        <button class="action-btn" title="Restock" onclick="document.getElementById('add-book-isbn').value='${b.isbn}'; app.ui.openModal('addBookModal');"><i class="fa-solid fa-plus"></i></button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            this.ui.initScrollAnimations();
        }
    },

    renderMembersTab(filterQuery = '') {
        const tbody = document.getElementById('members-list-tbody');
        const empty = document.getElementById('members-empty');
        const q = filterQuery.toLowerCase();
        
        const filtered = this.state.students.filter(s => 
            s.name.toLowerCase().includes(q) || s.id.toLowerCase().includes(q)
        );

        document.getElementById('members-count-label').textContent = `${filtered.length} active members`;

        tbody.innerHTML = '';
        if(filtered.length === 0) {
            empty.classList.remove('d-none');
        } else {
            empty.classList.add('d-none');
            const today = new Date().toISOString().split('T')[0];

            filtered.forEach(s => {
                let totalFine = 0;
                let hasOverdue = false;
                if(s.due_dates) {
                    s.due_dates.forEach(d => {
                        if(d && d < today) {
                            hasOverdue = true;
                            const days = Math.ceil((new Date(today) - new Date(d)) / 86400000);
                            totalFine += days * 30;
                        }
                    });
                }

                const fineBadge = totalFine > 0 ? `<span class="badge badge-danger">₹${totalFine}</span>` : `<span class="text-muted">—</span>`;
                const statusBadge = hasOverdue ? `<span class="badge badge-danger">Overdue</span>` : `<span class="badge badge-success">Active</span>`;
                
                let trustColorClass = "badge-success";
                if (s.trust_score < 50) trustColorClass = "badge-danger";
                else if (s.trust_score < 80) trustColorClass = "badge-warning";
                const trustBadge = `<span class="badge ${trustColorClass}" style="${trustColorClass === 'badge-warning' ? 'background:#fef3c7; color:#d97706;' : ''}"><i class="fa-solid fa-star" style="font-size:0.75rem; margin-right:3px;"></i>${s.trust_score}</span>`;

                const tr = document.createElement('tr');
                tr.className = 'scroll-anim';
                tr.innerHTML = `
                    <td>
                        <strong>${s.name}</strong>
                        <div class="text-muted" style="font-size:0.85rem">${s.id}</div>
                    </td>
                    <td>
                        <div style="background:var(--primary-light); color:var(--primary); padding:4px 10px; border-radius:12px; display:inline-block; font-weight:600; font-size:0.85rem;">
                            ${s.issued_books.length} / 3 Maximum
                        </div>
                    </td>
                    <td>${fineBadge}</td>
                    <td>${trustBadge}</td>
                    <td>${statusBadge}</td>
                    <td class="text-right">
                        <button class="action-btn edit" onclick="app.handlers.triggerEditMember('${s.id}', '${s.name.replace(/'/g, "\\'")}')"><i class="fa-solid fa-pen"></i></button>
                        <button class="action-btn delete" onclick="app.handlers.triggerDeleteMember('${s.id}')"><i class="fa-solid fa-trash"></i></button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            this.ui.initScrollAnimations();
        }
    },

    renderCirculationTab() {
        const tbody = document.getElementById('circulation-list-tbody');
        const empty = document.getElementById('circulation-empty');
        const pillCount = document.getElementById('overdue-pill-count');
        const today = new Date().toISOString().split('T')[0];

        // Overall Overdue Count for the Tab Pill
        const overdueCount = this.state.issued.filter(r => r.due_date && r.due_date < today).length;
        pillCount.textContent = overdueCount;

        // Filter for View
        let records = this.state.issued;
        if(this.state.circulationTab === 'overdue') {
            records = records.filter(r => r.due_date && r.due_date < today);
        } else if(this.state.circulationTab === 'issued') {
            records = records.filter(r => !r.due_date || r.due_date >= today);
        }

        tbody.innerHTML = '';
        if(records.length === 0) {
            empty.classList.remove('d-none');
        } else {
            empty.classList.add('d-none');
            records.forEach(r => {
                const isOverdue = r.due_date && r.due_date < today;
                let fine = '—';
                if(isOverdue) {
                    const daysOverdue = Math.ceil((new Date(today) - new Date(r.due_date)) / 86400000);
                    fine = `₹${daysOverdue * 30}`;
                }

                const statusBadge = isOverdue ? `<span class="badge badge-danger">Overdue</span>` : `<span class="badge badge-warning" style="background:#fef3c7; color:#d97706;">Issued</span>`;

                const tr = document.createElement('tr');
                tr.className = 'scroll-anim';
                tr.innerHTML = `
                    <td>
                        <strong class="text-primary">${r.book_title}</strong>
                        <div class="text-muted" style="margin-top:2px;">ISBN: ${r.isbn}</div>
                    </td>
                    <td>
                        <strong>${r.student_name}</strong>
                        <div class="text-muted" style="margin-top:2px;">${r.student_id}</div>
                    </td>
                    <td>${r.issue_date || '—'}</td>
                    <td class="${isOverdue ? 'text-danger fw-bold' : ''}">${r.due_date || '—'}</td>
                    <td><strong class="${isOverdue ? 'text-danger' : ''}">${fine}</strong></td>
                    <td>${statusBadge}</td>
                    <td class="text-right">
                        <button class="action-btn return" onclick="app.handlers.triggerReturn('${r.isbn}', '${r.student_id}')">
                            <i class="fa-solid fa-rotate-left"></i> Return
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            this.ui.initScrollAnimations();
        }
    },

    renderReportsTab() {
        const today = new Date().toISOString().split('T')[0];
        
        // 1. Calculate Status Breakdown
        let available = 0;
        let issued = 0;
        this.state.books.forEach(b => {
            available += b.available_copies;
            issued += (b.total_copies - b.available_copies);
        });

        // 2. Render Status Chart (Pie)
        const statusCtx = document.getElementById('reportsStatusChart');
        if(statusCtx) {
            if(this.state.reportsStatusChart) this.state.reportsStatusChart.destroy();
            this.state.reportsStatusChart = new Chart(statusCtx, {
                type: 'pie',
                data: {
                    labels: ['Available', 'Issued'],
                    datasets: [{
                        data: [available, issued],
                        backgroundColor: ['#10B981', '#F59E0B'],
                        borderWidth: 0
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // 3. Render Trend Chart (Line)
        const trendCtx = document.getElementById('reportsTrendChart');
        if(trendCtx) {
            if(this.state.reportsTrendChart) this.state.reportsTrendChart.destroy();
            this.state.reportsTrendChart = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Books Issued',
                        data: [12, 19, 3, 5, 2, 20], // Mock Data
                        borderColor: '#1E3A8A',
                        tension: 0.4,
                        fill: true,
                        backgroundColor: 'rgba(30, 58, 138, 0.1)'
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // 4. Render Top Borrowers
        const tbody = document.getElementById('reports-top-borrowers');
        if(tbody) {
            tbody.innerHTML = '';
            const sorted = [...this.state.students].sort((a, b) => b.issued_books.length - a.issued_books.length).slice(0, 5);
            
            sorted.forEach(s => {
                let fine = 0;
                if(s.due_dates) {
                    s.due_dates.forEach(d => {
                        if(d && d < today) {
                            fine += Math.ceil((new Date(today) - new Date(d)) / 86400000) * 30;
                        }
                    });
                }
                
                const tr = document.createElement('tr');
                tr.className = 'scroll-anim';
                tr.innerHTML = `
                    <td><strong>${s.name}</strong><br><small class="text-muted">${s.id}</small></td>
                    <td><span class="pill" style="background:var(--primary-light); color:var(--primary); font-weight:600;">${s.issued_books.length} Active</span></td>
                    <td><strong class="${fine > 0 ? 'text-danger' : ''}">₹${fine}</strong></td>
                    <td><span class="badge ${fine > 0 ? 'badge-danger' : 'badge-success'}">${fine > 0 ? 'Action Needed' : 'Waitlist Clear'}</span></td>
                `;
                tbody.appendChild(tr);
            });
            this.ui.initScrollAnimations();
        }
    },

    // Form Submissions & Handlers
    handlers: {
        async addBook(e) {
            e.preventDefault();
            const btn = document.getElementById('btn-submit-book');
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing';
            btn.disabled = true;

            const data = {
                title: document.getElementById('add-book-title').value,
                author: document.getElementById('add-book-author').value,
                isbn: document.getElementById('add-book-isbn').value,
                copies: parseInt(document.getElementById('add-book-copies').value)
            };

            try {
                const res = await fetch('/api/add', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                const result = await res.json();
                if(res.ok) {
                    app.ui.showToast(result.message);
                    app.ui.closeModal('addBookModal');
                    await app.fetchAllData();
                    app.refreshCurrentTab();
                } else {
                    app.ui.showToast(result.error, "error");
                }
            } catch(error) {
                app.ui.showToast("Network Error", "error");
            } finally {
                btn.innerHTML = 'Add Copies';
                btn.disabled = false;
            }
        },

        async addMember(e) {
            e.preventDefault();
            const data = {
                id: document.getElementById('add-member-id').value,
                name: document.getElementById('add-member-name').value
            };
            try {
                const res = await fetch('/api/add_student', {
                    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
                });
                const result = await res.json();
                if(res.ok) {
                    app.ui.showToast(result.message);
                    app.ui.closeModal('addMemberModal');
                    await app.fetchAllData();
                    app.refreshCurrentTab();
                } else app.ui.showToast(result.error, "error");
            } catch(e) { app.ui.showToast("Network Error", "error"); }
        },

        triggerEditMember(id, name) {
            document.getElementById('edit-member-id').value = id;
            document.getElementById('edit-member-name').value = name;
            app.ui.openModal('editMemberModal');
        },

        async editMember(e) {
            e.preventDefault();
            const id = document.getElementById('edit-member-id').value;
            const name = document.getElementById('edit-member-name').value;
            try {
                const res = await fetch('/api/edit_student', {
                    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({id, name})
                });
                if(res.ok) {
                    app.ui.showToast("Member updated successfully");
                    app.ui.closeModal('editMemberModal');
                    await app.fetchAllData();
                    app.refreshCurrentTab();
                } else app.ui.showToast("Failed to edit", "error");
            } catch(err) { app.ui.showToast("Network Error", "error"); }
        },

        triggerDeleteMember(id) {
            const btn = document.getElementById('btn-confirm-delete');
            // Clean up old listeners
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            
            newBtn.addEventListener('click', async () => {
                newBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Deleting';
                newBtn.disabled = true;
                try {
                    const res = await fetch(`/api/delete_student/${id}`, { method: 'DELETE' });
                    const result = await res.json();
                    if(res.ok) {
                        app.ui.showToast(result.message);
                        app.ui.closeModal('deleteConfirmModal');
                        await app.fetchAllData();
                        app.refreshCurrentTab();
                    } else app.ui.showToast(result.error, "error");
                } catch(e) { app.ui.showToast("Network Error", "error"); }
            });
            app.ui.openModal('deleteConfirmModal');
        },

        async issueBook(e) {
            e.preventDefault();
            const data = {
                isbn: document.getElementById('issue-isbn').value,
                student_id: document.getElementById('issue-student').value,
                duration_days: parseInt(document.getElementById('issue-duration').value) || 14
            };
            try {
                const res = await fetch('/api/issue', {
                    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)
                });
                const result = await res.json();
                if(res.ok) {
                    app.ui.showToast(result.message);
                    app.ui.closeModal('issueBookModal');
                    await app.fetchAllData();
                    app.refreshCurrentTab();
                } else app.ui.showToast(result.error, "error");
            } catch(e) { app.ui.showToast("Network Error", "error"); }
        },

        triggerReturn(isbn, student_id) {
            const record = app.state.issued.find(r => r.isbn === isbn && r.student_id === student_id);
            if(!record) return;

            document.getElementById('return-modal-isbn').value = isbn;
            document.getElementById('return-modal-student').value = student_id;
            
            document.getElementById('return-book-title').textContent = record.book_title;
            document.getElementById('return-student-name').textContent = record.student_name;
            document.getElementById('return-student-id').textContent = record.student_id;

            const today = new Date().toISOString().split('T')[0];
            const isOverdue = record.due_date && record.due_date < today;

            const alertBox = document.getElementById('return-fine-alert');
            const confirmBtn = document.getElementById('btn-confirm-return');
            
            if(isOverdue) {
                const daysOverdue = Math.ceil((new Date(today) - new Date(record.due_date)) / 86400000);
                const fine = daysOverdue * 30;
                document.getElementById('return-fine-amount').textContent = `₹${fine}`;
                alertBox.classList.remove('d-none');
                confirmBtn.textContent = "Confirm Payment & Return";
            } else {
                alertBox.classList.add('d-none');
                confirmBtn.textContent = "Confirm Return";
            }

            // Button listener
            const newBtn = confirmBtn.cloneNode(true);
            confirmBtn.parentNode.replaceChild(newBtn, confirmBtn);

            newBtn.addEventListener('click', async () => {
                newBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Returning';
                newBtn.disabled = true;
                try {
                    const res = await fetch('/api/return', {
                        method: 'POST', headers: {'Content-Type': 'application/json'}, 
                        body: JSON.stringify({isbn, student_id})
                    });
                    const result = await res.json();
                    if(res.ok) {
                        app.ui.showToast(result.message);
                        app.ui.closeModal('returnBookModal');
                        await app.fetchAllData();
                        app.refreshCurrentTab();
                    } else app.ui.showToast(result.error, "error");
                } catch(e) { 
                    app.ui.showToast("Network Error", "error"); 
                } finally {
                    newBtn.disabled = false;
                }
            });

            app.ui.openModal('returnBookModal');
        },

        async saveAdminSettings(e) {
            e.preventDefault();
            const newName = document.getElementById('admin-name-input').value;
            const newRole = document.getElementById('admin-role-input').value;
            
            // Update Sidebar
            const sidebarName = document.querySelector('.user-profile-sidebar .name');
            const sidebarRole = document.querySelector('.user-profile-sidebar .role');
            const sidebarImg = document.querySelector('.user-profile-sidebar img');
            
            if(sidebarName) sidebarName.textContent = newName;
            if(sidebarRole) sidebarRole.textContent = newRole;
            
            const newAvatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(newName)}&background=1E3A8A&color=fff`;
            if(sidebarImg) sidebarImg.src = newAvatar;
            
            // Update Modal Preview
            const modalImg = document.getElementById('admin-preview-img');
            if(modalImg) modalImg.src = newAvatar;
            
            app.ui.showToast("Admin profile updated successfully");
            app.ui.closeModal('adminSettingsModal');
        }
    }
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
