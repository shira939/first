import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { AppComponent } from './app.component';
import { FileUploadComponent } from './file-upload/file-upload.component';
import { HttpClientModule } from '@angular/common/http'; // ייבוא HttpClientModule

@NgModule({
  declarations: [
    // AppComponent,
    // FileUploadComponent
  ],
  imports: [
    BrowserModule,
    AppComponent,
    FileUploadComponent,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [] // שינוי כאן
})
export class AppModule { }