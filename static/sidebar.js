
document.addEventListener("DOMContentLoaded", function () {
    const wrapper = document.querySelector(".page.wrapper");
    const showSidebarBtn = document.getElementById("show-sidebar");
    const closeSidebarBtn = document.getElementById("close-sidebar");

    function updateSidebarOnResize() {
        if (window.innerWidth <= 768) {
            wrapper.classList.add("toggled");
        } else {
            wrapper.classList.remove("toggled");
        }
    }

    updateSidebarOnResize();
    window.addEventListener("resize", updateSidebarOnResize);

    if (showSidebarBtn) {
        showSidebarBtn.addEventListener("click", function (e) {
            e.preventDefault();
            wrapper.classList.remove("toggled");
        });
    }

    if (closeSidebarBtn) {
        closeSidebarBtn.addEventListener("click", function () {
            wrapper.classList.add("toggled");
        });
    }

    // Sidebar dropdown aç/kapat
    document.querySelectorAll('.sidebar-dropdown > a').forEach(menu => {
        menu.addEventListener('click', function (e) {
            const parent = this.parentElement;
            const submenu = parent.querySelector('.sidebar-submenu');
            const isActive = parent.classList.contains('active');

            if (!submenu || this.getAttribute('href') !== '#') return;

            e.preventDefault();

            document.querySelectorAll('.sidebar-dropdown').forEach(item => {
                item.classList.remove('active');
                const sm = item.querySelector('.sidebar-submenu');
                if (sm) sm.style.display = 'none';
            });

            if (!isActive) {
                parent.classList.add('active');
                if (submenu) submenu.style.display = 'block';
            }
        });
    });
});
