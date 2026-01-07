import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { AnalysisService } from '../../../../core/services/analysis.service';
import { MoviesService } from '../../../../core/services/movies.service';
import { Movie } from '../../../../core/models/movie.model';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-movie-list',
  standalone: false,
  templateUrl: './movie-list.html',
  styleUrls: ['./movie-list.scss'],
})
export class MovieListComponent implements OnInit {
  movies$: Observable<Movie[]> | null = null;
  page = 0;
  pageSize = 20;
  sort = 'title';
  filters: any = {};

  constructor(
    private moviesService: MoviesService,
    private analysisService: AnalysisService,
    private cdr: ChangeDetectorRef
  ) { }

  ngOnInit() {
    // Subscribe to filter changes
    this.analysisService.activeFilters$.subscribe(filters => {
      this.filters = filters;
      this.page = 0; // Reset page on filter change
      this.loadMovies();
    });
  }

  loadMovies() {
    // We now use searchMovies for everything to ensure In-Memory sorting (Year) works correctly
    // even without filters.
    this.movies$ = this.moviesService.searchMovies(
      this.filters,
      this.pageSize,
      this.page * this.pageSize,
      this.sort
    );
  }

  nextPage() {
    this.page++;
    this.loadMovies();
  }

  prevPage() {
    if (this.page > 0) {
      this.page--;
      this.loadMovies();
    }
  }

  selectedMovies: Movie[] = [];
  showComparisonModal = false;
  comparisonData: any[] = [];

  toggleSelection(movie: Movie) {
    const index = this.selectedMovies.findIndex(m => m.id === movie.id);
    if (index >= 0) {
      this.selectedMovies.splice(index, 1);
    } else {
      if (this.selectedMovies.length < 3) {
        this.selectedMovies.push(movie);
      }
    }
  }

  isSelected(movie: Movie): boolean {
    return this.selectedMovies.some(m => m.id === movie.id);
  }

  openComparisonModal() {
    if (this.selectedMovies.length < 2) return;

    const ids = this.selectedMovies.map(m => m.id);
    this.moviesService.compareMovies(ids).subscribe(data => {
      this.comparisonData = data;
      this.showComparisonModal = true;
      this.cdr.detectChanges();
    });
  }

  closeComparisonModal() {
    this.showComparisonModal = false;
    this.comparisonData = [];
  }

  onSortChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    this.sort = target.value;
    this.page = 0;
    this.loadMovies();
  }
}
