import { Component } from '@angular/core';
import { SidebarService } from '../../services/sidebar.service';

@Component({
    selector: 'app-sidebar',
    templateUrl: './sidebar.component.html',
    styleUrls: ['./sidebar.component.scss'],
    standalone: false
})
export class SidebarComponent {
    constructor(private sidebarService: SidebarService) { }

    closeSidebar() {
        this.sidebarService.close();
    }
}
