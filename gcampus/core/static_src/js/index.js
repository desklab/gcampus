/*
 * Copyright (C) 2021-2022 desklab gUG (haftungsbeschränkt)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import Tooltip from 'bootstrap/js/src/tooltip';
import Collapse from 'bootstrap/js/src/collapse';
import Dropdown from 'bootstrap/js/src/dropdown';
import 'bootstrap/js/src/modal';
import Alert from 'bootstrap/js/src/alert';
import Toast from 'bootstrap/js/src/toast';
import 'bootstrap/js/src/util';


import '../styles/main.scss';


const SIDEBAR_STATE_COOKIE_NAME = window.SIDEBAR_STATE_COOKIE_NAME;
const TIME_ZONE_COOKIE_NAME = window.TIME_ZONE_COOKIE_NAME;
const sidebarElement = document.getElementById('sidebar');
const sidebarControl = document.querySelector('[aria-controls="sidebar"]');


function setCookie(name, value, days) {
    const expirationDate = new Date();
    expirationDate.setTime(
        expirationDate.getTime()
        + (days * 24 * 60 * 60 * 1000)
    );
    let expires = 'expires=' + expirationDate.toUTCString();
    document.cookie = name + '=' + value + ';' + expires + ';samesite=lax;path=/';
}

function getCookie(name) {
    let cookies = document.cookie.split(';');
    if (cookies === undefined || cookies.length === 0)
        return null;
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i];
        if (cookie.startsWith(' ')) {
            // Remove space at the beginning
            cookie.substring(1);
        }
        if (cookie.startsWith(name)) {
            return cookie.split('=')[1];
        }
    }
    return null;
}

function setSidebarCookie(state) {
    setCookie(SIDEBAR_STATE_COOKIE_NAME, (state) ? "1" : "0", 90);
}


function toggleSidebar() {
    let open = sidebarElement.classList.toggle('show-sidebar');
    setSidebarCookie(open);
    sidebarControl.setAttribute("aria-expanded", open);
}


function setup() {
    // Setup timezone cookie
    let timeZone = new Intl.DateTimeFormat().resolvedOptions().timeZone;
    setCookie(TIME_ZONE_COOKIE_NAME, timeZone);

    // Setup tooltips
    let tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new Tooltip(tooltipTriggerEl);
    });

    // Setup sidebar
    let desiredSidebarState = getCookie(SIDEBAR_STATE_COOKIE_NAME);
    if (desiredSidebarState === '1') {
        document.getElementById('sidebar').classList.add('show-sidebar');
        sidebarControl.setAttribute("aria-expanded", true);
    } else if (desiredSidebarState === '0') {
        document.getElementById('sidebar').classList.remove('show-sidebar');
        sidebarControl.setAttribute("aria-expanded", false);
    }

    sidebarElement.addEventListener('hide.bs.collapse', () => setSidebarCookie(false));
    sidebarElement.addEventListener('show.bs.collapse', () => setSidebarCookie(true));

    const mainContent = document.querySelector('main');
    if (mainContent !== undefined) {
        mainContent.addEventListener('transitionend', function () {
            for (let map in window._maps) {
                window._maps[map].resize();
            }
        });
    }
}

setup();

export {Toast, Tooltip, toggleSidebar};
