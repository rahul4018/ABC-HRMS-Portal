(function () {
    'use strict';

    const body = document.body;
    const sidebar = document.getElementById('sidebar-wrapper');
    const nav = document.getElementById('sidebarNav');
    const mobileToggle = document.getElementById('sidebarToggleButton');
    const collapseToggle = document.getElementById('sidebarCollapseToggle');
    const overlay = document.getElementById('mobileSidebarOverlay');
    const desktop = window.matchMedia('(min-width: 992px)');
    const storageKey = 'ABC HRMS Portal.sidebar.collapsed';

    if (!sidebar || !nav) return;

    function setMobileOpen(open) {
        body.classList.toggle('sidebar-open', open);
        if (mobileToggle) mobileToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        if (overlay) overlay.setAttribute('aria-hidden', open ? 'false' : 'true');
    }

    function setCollapsed(collapsed) {
        if (!desktop.matches) return;
        body.classList.toggle('sc-sidebar-collapsed', collapsed);
        localStorage.setItem(storageKey, collapsed ? '1' : '0');
        if (collapseToggle) {
            collapseToggle.setAttribute('aria-label', collapsed ? 'Expand navigation' : 'Collapse navigation');
            collapseToggle.setAttribute('title', collapsed ? 'Expand navigation' : 'Collapse navigation');
            const icon = collapseToggle.querySelector('i');
            if (icon) icon.className = collapsed ? 'bi bi-layout-sidebar-inset-reverse' : 'bi bi-layout-sidebar-inset';
        }
    }

    function restoreState() {
        if (desktop.matches) setCollapsed(localStorage.getItem(storageKey) === '1');
        else body.classList.remove('sc-sidebar-collapsed');
    }

    function markActiveNav() {
        const currentPath = (window.location.pathname || '/').replace(/\/$/, '/') || '/';
        let best = null;
        let bestLength = -1;

        document.querySelectorAll('.sc-nav-link[data-nav-path]').forEach(function (link) {
            link.classList.remove('active');
            link.removeAttribute('aria-current');
            const raw = link.getAttribute('data-nav-path');
            if (!raw) return;
            const target = raw.endsWith('/') ? raw : raw + '/';
            const match = currentPath === target || (target !== '/' && currentPath.startsWith(target));
            if (match && target.length > bestLength) {
                best = link;
                bestLength = target.length;
            }
        });

        if (best) {
            best.classList.add('active');
            best.setAttribute('aria-current', 'page');
            const parent = best.closest('details.sc-nav-section');
            if (parent) parent.open = true;
        }
    }

    if (collapseToggle) {
        collapseToggle.addEventListener('click', function () {
            setCollapsed(!body.classList.contains('sc-sidebar-collapsed'));
        });
    }

    if (mobileToggle) {
        mobileToggle.addEventListener('click', function () {
            if (desktop.matches) {
                setCollapsed(!body.classList.contains('sc-sidebar-collapsed'));
            } else {
                setMobileOpen(!body.classList.contains('sidebar-open'));
            }
        });
    }

    if (overlay) overlay.addEventListener('click', function () { setMobileOpen(false); });

    nav.addEventListener('wheel', function (event) {
        // Make the navigation a reliable wheel-scroll target even when a parent
        // component has captured overflow. Only intervene when the nav can scroll.
        if (nav.scrollHeight > nav.clientHeight) event.stopPropagation();
    }, { passive: true });

    nav.querySelectorAll('a.sc-nav-link').forEach(function (link) {
        link.addEventListener('click', function () {
            if (!desktop.matches) setMobileOpen(false);
        });
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') setMobileOpen(false);
        if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey) {
            const target = event.target;
            const tag = target && target.tagName ? target.tagName.toLowerCase() : '';
            if (!['input', 'textarea', 'select'].includes(tag) && target && !target.isContentEditable) {
                const search = document.querySelector('.sc-search-input');
                if (search) { event.preventDefault(); search.focus(); }
            }
        }
    });

    desktop.addEventListener('change', function (event) {
        if (event.matches) {
            setMobileOpen(false);
            setCollapsed(localStorage.getItem(storageKey) === '1');
        } else {
            body.classList.remove('sc-sidebar-collapsed');
        }
    });

    restoreState();
    markActiveNav();
})();
