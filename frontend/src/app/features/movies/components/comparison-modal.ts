import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-comparison-modal',
  standalone: false,
  templateUrl: './comparison-modal.html',
  styleUrls: ['./comparison-modal.scss']
})
export class ComparisonModalComponent {
  @Input() data: any[] = [];
  @Output() close = new EventEmitter<void>();

  onClose() {
    this.close.emit();
  }
}
