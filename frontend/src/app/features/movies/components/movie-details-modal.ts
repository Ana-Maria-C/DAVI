import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-movie-details-modal',
  standalone: false,
  templateUrl: './movie-details-modal.html',
  styleUrls: ['./movie-details-modal.scss']
})
export class MovieDetailsModalComponent {
  @Input() movie: any;
  @Output() close = new EventEmitter<void>();

  onClose() {
    this.close.emit();
  }
}
