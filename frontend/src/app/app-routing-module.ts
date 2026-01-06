import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ShellComponent } from './core/components/shell/shell.component';
import { HomeComponent } from './features/home/home';

const routes: Routes = [
  {
    path: '',
    component: ShellComponent,
    children: [
      { path: '', component: HomeComponent },
      {
        path: 'movies',
        loadChildren: () => import('./features/movies/movies-module').then(m => m.MoviesModule)
      },
      {
        path: 'resource',
        loadChildren: () => import('./features/resource-viewer/resource-viewer-module').then(m => m.ResourceViewerModule)
      },
      {
        path: 'sparql',
        loadChildren: () => import('./features/sparql/sparql-module').then(m => m.SparqlModule)
      }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
