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

  // Helper method removed as API now returns generic Movie objects directly
  private transformBindings(bindings: any[]): Movie[] {
    return bindings; // No-op if needed, but better to remove usage
  }
}
