import { Component, OnInit, ChangeDetectorRef, NgZone } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';
import { AnalysisService } from '../../../../core/services/analysis.service';
import { MoviesService } from '../../../../core/services/movies.service';
import { Movie } from '../../../../core/models/movie.model';

@Component({
  selector: 'app-movie-list',
  standalone: false,
  templateUrl: './movie-list.html',
  styleUrls: ['./movie-list.scss'],
})
export class MovieListComponent implements OnInit {
  movies: Movie[] = [];
  isLoading = false;
  page = 0;
  pageSize = 20;
  sort = 'title';
  filters: any = {};
  searchTitle: string = '';

  constructor(
    private moviesService: MoviesService,
    private analysisService: AnalysisService,
    private cdr: ChangeDetectorRef,
    private zone: NgZone,
    private route: ActivatedRoute,
    private location: Location
  ) { }

  ngOnInit() {
    // Subscribe to filter changes
    this.analysisService.activeFilters$.subscribe(filters => {
      this.filters = filters;
      this.page = 0; // Reset page on filter change
      this.loadMovies();
    });

    // Check for ID in route
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        // If we have an ID, we need to load that specific movie's details
        // We can create a temporary movie object with just the ID to trigger openDetails
        // openDetails will fetch the full data anyway
        const tempMovie = { id: id } as Movie;
        this.openDetails(tempMovie);
      }
    });
  }

  loadMovies() {
    this.isLoading = true;

    if (this.searchTitle && this.searchTitle.trim().length > 0) {
      this.moviesService.searchMoviesByTitle(this.searchTitle, this.filters).subscribe({
        next: (data) => {
          this.zone.run(() => {
            this.movies = data;
            this.isLoading = false;
            this.cdr.detectChanges();
          });
        },
        error: (err) => {
          console.error('Error searching movies:', err);
          this.isLoading = false;
          this.cdr.detectChanges();
        }
      });
    } else {
      this.moviesService.searchMovies(
        this.filters,
        this.pageSize,
        this.page * this.pageSize,
        this.sort
      ).subscribe({
        next: (data) => {
          this.zone.run(() => {
            this.movies = data;
            this.isLoading = false;
            this.cdr.detectChanges();
          });
        },
        error: (err) => {
          console.error('Error loading movies:', err);
          this.isLoading = false;
          this.cdr.detectChanges();
        }
      });
    }
  }

  onSearchChange() {
    this.page = 0;
    this.loadMovies();
  }

  nextPage() {
    this.page++;
    if (this.searchTitle) {
      // Pagination for search results is not yet implemented in backend/service for title search 
      // based on current simplified implementation (it returns all matches with limit).
      // We'll keep it simple for now or disable pagination in search mode.
      console.warn('Pagination not fully supported for title search in this iteration');
    }
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
      this.zone.run(() => {
        this.comparisonData = data;
        this.showComparisonModal = true;
        this.cdr.detectChanges();
      });
    });
  }

  closeComparisonModal() {
    this.showComparisonModal = false;
    this.comparisonData = [];
  }

  showDetailsModal = false;
  selectedDetailsMovie: any = null;

  openDetails(movie: Movie) {
    // Update URL without reloading
    this.location.go(`/movies/${movie.id}`);

    this.moviesService.getMovieById(movie.id).subscribe({
      next: (data) => {
        setTimeout(() => {
          this.zone.run(() => {
            // Extract year if missing, or use from list
            let year = 'Unknown';
            if (data.title) {
              const match = data.title.match(/\((\d{4})\)/);
              if (match) {
                year = match[1];
              }
            }

            this.selectedDetailsMovie = { ...data, year };
            this.showDetailsModal = true;
            this.cdr.detectChanges();
          });
        }, 0);
      },
      error: (err) => console.error('Error fetching details:', err)
    });
  }

  closeDetails() {
    this.showDetailsModal = false;
    this.selectedDetailsMovie = null;
    // Revert URL
    this.location.go('/movies');
  }

  onSortChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    this.sort = target.value;
    this.page = 0;
    this.loadMovies();
  }
}
