import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
    selector: 'app-button',
    templateUrl: './button.component.html',
    styleUrls: ['./button.component.scss'],
    standalone: false
})
export class ButtonComponent {
    @Input() type: 'button' | 'submit' | 'reset' = 'button';
    @Input() variant: 'primary' | 'secondary' | 'outline' = 'primary';
    @Input() disabled = false;
    @Output() onClick = new EventEmitter<Event>();

    handleClick(event: Event) {
        if (!this.disabled) {
            this.onClick.emit(event);
        }
    }
}
