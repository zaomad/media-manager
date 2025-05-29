// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 初始化弹出框
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // 添加淡入效果
    document.querySelectorAll('.card').forEach(function(card) {
        card.classList.add('fade-in');
    });

    // 处理删除确认
    var deleteModal = document.getElementById('deleteModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function(event) {
            var button = event.relatedTarget;
            var itemTitle = button.getAttribute('data-title');
            var modalBodyInput = deleteModal.querySelector('.modal-body');
            if (itemTitle) {
                modalBodyInput.textContent = '确定要删除"' + itemTitle + '"吗？此操作不可撤销。';
            }
        });
    }

    // 处理表单验证
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // 图片错误处理
    document.querySelectorAll('img').forEach(function(img) {
        img.addEventListener('error', function() {
            // 图片加载失败时替换为默认图标
            var parent = this.parentElement;
            var type = parent.getAttribute('data-type') || 'book';
            var icon = '';
            
            if (type === 'book') {
                icon = 'bi-book';
            } else if (type === 'movie') {
                icon = 'bi-film';
            } else if (type === 'music') {
                icon = 'bi-music-note-beamed';
            }
            
            var placeholder = document.createElement('div');
            placeholder.className = 'card-img-top bg-light d-flex align-items-center justify-content-center';
            placeholder.style.height = '200px';
            placeholder.innerHTML = '<i class="bi ' + icon + '" style="font-size: 3rem;"></i>';
            
            parent.replaceChild(placeholder, this);
        });
    });

    // 处理排序功能
    var sortSelects = document.querySelectorAll('select[name="sortBy"]');
    sortSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            var sortBy = this.value;
            var container = this.closest('.container').querySelector('.row.row-cols-1');
            var items = Array.from(container.querySelectorAll('.col'));
            
            items.sort(function(a, b) {
                var aValue = a.getAttribute('data-' + sortBy) || '';
                var bValue = b.getAttribute('data-' + sortBy) || '';
                
                // 数字排序
                if (!isNaN(aValue) && !isNaN(bValue)) {
                    return Number(aValue) - Number(bValue);
                }
                
                // 字符串排序
                return aValue.localeCompare(bValue);
            });
            
            // 清空容器并按排序后的顺序重新添加元素
            items.forEach(function(item) {
                container.appendChild(item);
            });
        });
    });
    
    // 视图切换功能
    const viewButtons = document.querySelectorAll('.view-toggle .btn');
    if (viewButtons.length > 0) {
        // 从本地存储加载视图偏好
        const preferredView = localStorage.getItem('preferredView') || 'grid';
        
        // 初始化视图
        updateView(preferredView);
        
        // 添加点击事件监听器
        viewButtons.forEach(button => {
            button.addEventListener('click', function() {
                // 更新按钮状态
                viewButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // 获取视图类型
                const viewType = this.getAttribute('data-view');
                
                // 更新视图
                updateView(viewType);
                
                // 保存到本地存储
                localStorage.setItem('preferredView', viewType);
            });
        });
    }
    
    // 表格排序功能
    const tables = document.querySelectorAll('.table-sortable');
    if (tables.length > 0) {
        tables.forEach(table => {
            const headers = table.querySelectorAll('thead th');
            headers.forEach((header, index) => {
                if (index > 0) { // 跳过第一列（通常是图片或编号）
                    header.addEventListener('click', function() {
                        sortTable(table, index);
                    });
                    header.style.cursor = 'pointer';
                    header.title = '点击排序';
                }
            });
        });
    }

    // 主题切换功能
    // 检查本地存储中的主题设置
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // 应用主题类到body元素
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }
    
    // 更新主题图标
    updateThemeIcon(savedTheme);
    
    // 主题切换按钮点击事件
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // 更新主题
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // 切换body类
            if (newTheme === 'dark') {
                document.body.classList.add('dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
            }
            
            // 更新图标
            updateThemeIcon(newTheme);
        });
    }
    
    // 私密页面切换按钮点击事件
    const privateToggle = document.getElementById('private-toggle');
    const privateNavbar = document.getElementById('private-navbar');
    const privateClose = document.getElementById('private-close');
    
    if (privateToggle && privateNavbar && privateClose) {
        privateToggle.addEventListener('click', function() {
            privateNavbar.style.display = 'block';
            // 添加动画效果
            setTimeout(function() {
                privateNavbar.style.opacity = '1';
            }, 10);
        });
        
        privateClose.addEventListener('click', function() {
            privateNavbar.style.opacity = '0';
            setTimeout(function() {
                privateNavbar.style.display = 'none';
            }, 300);
        });
    }
});

// 更新视图显示
function updateView(viewType) {
    const mediaContainer = document.querySelector('.media-container');
    if (mediaContainer) {
        // 移除所有视图类
        mediaContainer.classList.remove('grid-view', 'list-view', 'table-view');
        // 添加当前视图类
        mediaContainer.classList.add(viewType + '-view');
        
        // 显示/隐藏相应内容
        document.querySelectorAll('.view-content').forEach(content => {
            content.style.display = 'none';
        });
        
        const activeContent = document.querySelector('.' + viewType + '-content');
        if (activeContent) {
            activeContent.style.display = 'block';
        }
    }
}

// 表格排序功能
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // 确定排序方向
    const currentOrder = tbody.getAttribute('data-order') || 'asc';
    const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
    
    // 排序行
    rows.sort((a, b) => {
        let aValue = a.cells[columnIndex].textContent.trim();
        let bValue = b.cells[columnIndex].textContent.trim();
        
        // 尝试将值转换为数字进行比较
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return newOrder === 'asc' ? aNum - bNum : bNum - aNum;
        }
        
        // 字符串比较
        return newOrder === 'asc' 
            ? aValue.localeCompare(bValue) 
            : bValue.localeCompare(aValue);
    });
    
    // 更新表格
    rows.forEach(row => tbody.appendChild(row));
    
    // 更新排序方向
    tbody.setAttribute('data-order', newOrder);
    
    // 更新表头指示器
    const headers = table.querySelectorAll('thead th');
    headers.forEach(header => {
        header.classList.remove('sorted-asc', 'sorted-desc');
    });
    
    headers[columnIndex].classList.add(newOrder === 'asc' ? 'sorted-asc' : 'sorted-desc');
}

// 更新主题图标
function updateThemeIcon(theme) {
    const lightIcon = document.querySelector('.theme-icon-light');
    const darkIcon = document.querySelector('.theme-icon-dark');
    
    if (lightIcon && darkIcon) {
        if (theme === 'dark') {
            lightIcon.classList.add('d-none');
            darkIcon.classList.remove('d-none');
        } else {
            darkIcon.classList.add('d-none');
            lightIcon.classList.remove('d-none');
        }
    }
} 