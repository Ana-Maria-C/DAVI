import { Component, OnInit } from '@angular/core';
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

  constructor(private moviesService: MoviesService) { }

  ngOnInit() {
    this.loadMovies();
  }

  loadMovies() {
    this.movies$ = this.moviesService.getMovies(this.page * this.pageSize, this.pageSize, this.sort);
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

  onSortChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    this.sort = target.value;
    this.page = 0;
    this.loadMovies();
  }
}
