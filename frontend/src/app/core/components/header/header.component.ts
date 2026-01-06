import { Component } from '@angular/core';
import { ThemeService } from '../../services/theme.service';
import { SidebarService } from '../../services/sidebar.service';

@Component({
    selector: 'app-header',
    templateUrl: './header.component.html',
    styleUrls: ['./header.component.scss'],
    standalone: false
})
export class HeaderComponent {
    constructor(public themeService: ThemeService, private sidebarService: SidebarService) { }

    toggleSidebar() {
        this.sidebarService.toggle();
    }
}
