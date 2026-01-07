import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiService } from './api.service';
import { Movie } from '../models/movie.model';

@Injectable({
  providedIn: 'root'
})
export class MoviesService {

  constructor(private api: ApiService) { }

  getMovies(offset: number = 0, limit: number = 20, sort: string = 'title'): Observable<Movie[]> {
    return this.api.get<Movie[]>('/api/movies', {
      limit: limit.toString(),
      offset: offset.toString(),
      sort
    });
  }

  searchMovies(filters: any, limit: number = 20, offset: number = 0, sort: string = 'title'): Observable<Movie[]> {
    const params: any = {
      limit: limit.toString(),
      offset: offset.toString(),
      sort: sort
    };
    if (filters.genre) params.genre = filters.genre;
    if (filters.yearMin) params.year_min = filters.yearMin.toString();
    if (filters.yearMax) params.year_max = filters.yearMax.toString();
    if (filters.ratingMin) params.rating_min = filters.ratingMin.toString();
    if (filters.ratingMax) params.rating_max = filters.ratingMax.toString();

    return this.api.get<Movie[]>('/api/movies/search', params);
  }

  // Helper method removed as API now returns generic Movie objects directly
  compareMovies(ids: string[]): Observable<any[]> {
    return this.api.get<any[]>('/api/movies/compare', { ids: ids });
  }

  getMovieById(id: string): Observable<any> {
    return this.api.get<any>(`/api/movies/${id}`);
  }
}
