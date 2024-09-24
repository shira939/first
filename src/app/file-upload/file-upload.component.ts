// import { Component } from '@angular/core';
// import { HttpClient } from '@angular/common/http';
// import { CommonModule } from '@angular/common';
// import { HttpClientModule } from '@angular/common/http';

// @Component({
//   selector: 'app-file-upload',
//   standalone: true,
//   imports: [CommonModule, HttpClientModule],
//   templateUrl: './file-upload.component.html',
//   styleUrls: ['./file-upload.component.css']
// })
// export class FileUploadComponent {
//   selectedFile: File | null = null;
//   scanResult: any = null;
//   threatEngines: string[] = [];

//   constructor(private http: HttpClient) {}

//   onFileSelected(event: any) {
//     this.selectedFile = event.target.files[0];
//   }

//   onUpload() {
//     if (!this.selectedFile) return;

//     const formData = new FormData();
//     formData.append('file', this.selectedFile, this.selectedFile.name);

//     // שליחת בקשה לשרת
//     this.http.post('http://localhost:8000/uploadfile/', formData, { observe: 'response' })
//       .subscribe({
//         next: (response: any) => {
//           this.scanResult = response.body;
//           // בדיקה אם קיימים פרטי איומים
//           if (this.scanResult?.scan_result?.threat_details) {
//             this.threatEngines = Object.keys(this.scanResult.scan_result.threat_details);
//           }
//         },
//         error: (error: any) => {
//           console.error('Upload failed:', error);
//         }
//       });
//   }
// }

import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [CommonModule, HttpClientModule],
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css']
})
export class FileUploadComponent {
  selectedFile: File | null = null;
  scanResult: any = null;
  threatEngines: string[] = [];
  fileSelected = false;  // מצב קובץ נבחר
  uploadInProgress = false;  // מצב העלאה

  constructor(private http: HttpClient) {}

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
    this.fileSelected = !!this.selectedFile;  // קובץ נבחר
  }

  onUpload() {
    if (!this.selectedFile) return;

    this.uploadInProgress = true;  // התחלת תהליך העלאה
    const formData = new FormData();
    formData.append('file', this.selectedFile, this.selectedFile.name);

    this.http.post('http://localhost:8000/uploadfile/', formData, { observe: 'response' })
      .subscribe({
        next: (response: any) => {
          this.scanResult = response.body;
          this.uploadInProgress = false;  // סיום תהליך העלאה
          if (this.scanResult?.scan_result?.threat_details) {
            this.threatEngines = Object.keys(this.scanResult.scan_result.threat_details);
          }
        },
        error: (error: any) => {
          console.error('Upload failed:', error);
          this.uploadInProgress = false;  // סיום תהליך העלאה במקרה של שגיאה
        }
      });
  }
}
