import { Component } from '@angular/core';
import { SidebarService } from '../../services/sidebar.service';
import { Observable } from 'rxjs';

@Component({
    selector: 'app-shell',
    templateUrl: './shell.component.html',
    styleUrls: ['./shell.component.scss'],
    standalone: false
})
export class ShellComponent {
    isSidebarOpen$: Observable<boolean>;

    constructor(private sidebarService: SidebarService) {
        this.isSidebarOpen$ = this.sidebarService.isOpen$;
    }

    closeSidebar() {
        this.sidebarService.close();
    }
}
