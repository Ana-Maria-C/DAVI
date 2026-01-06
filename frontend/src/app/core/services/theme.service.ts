import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class ThemeService {
    // Default to Light Mode (false)
    private _darkMode = new BehaviorSubject<boolean>(false);
    darkMode$ = this._darkMode.asObservable();

    constructor() {
        this.syncTheme();
    }

    toggleTheme() {
        this._darkMode.next(!this._darkMode.value);
        this.syncTheme();
    }

    private syncTheme() {
        if (this._darkMode.value) {
            document.body.classList.add('dark-theme');
        } else {
            document.body.classList.remove('dark-theme');
        }
    }
}
