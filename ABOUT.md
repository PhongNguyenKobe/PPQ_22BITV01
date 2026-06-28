# 📦 PPQ – Software Engineering Special Project 2

## 👨‍💻 Thành viên nhóm
- **Nguyễn Đặng Thanh Phong** – 2200002381  
- **Võ Toàn Phú** – 2200003893  
- **Trần Thanh Quang** – 2200002464 



# Vue 3 + TypeScript + Vite
This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.
Learn more about the recommended Project Setup and IDE Support in the [Vue Docs TypeScript Guide](https://vuejs.org/guide/typescript/overview.html#project-setup).


<div align="center">

# 📖 NỘI DUNG HỌC TẬP TỪNG BUỔI

</div>

# ✨ Tuần 1 – Khởi động dự án 

## 🚀 Session 01 – Project Initialization 08/06/2026
**Mục tiêu:**  
- Hiểu kiến trúc **Full-Stack** và thiết lập môi trường phát triển.  

**Lý thuyết:**  
- [Web Architecture](ca://s?q=Gi%E1%BA%A3i_th%C3%ADch_Web_Architecture)  
- [Frontend](ca://s?q=Frontend_l%C3%A0_g%C3%AC)  
- [Backend](ca://s?q=Backend_l%C3%A0_g%C3%AC)  
- [Database](ca://s?q=Database_trong_Fullstack)  
- [HTTP](ca://s?q=HTTP_l%C3%A0_g%C3%AC)  
- [Git Fundamentals](ca://s?q=Git_c%C6%A1_b%E1%BA%A3n) → Repository, Commit, Push  

**Thực hành:**  
- Tạo 2 project: `frontend/` và `backend/`  
- Khởi tạo GitHub repository  
- Thực hiện:  
  ```bash
  git init
  git add .
  git commit
  git push

## 🎨 Session 02 – Landing Page 12/06/2026

**Mục tiêu:**  
- Học các khái niệm cơ bản về **React** và phát triển theo hướng **component-based**.  

**Lý thuyết:**  
- [ES6](ca://s?q=ES6_trong_JavaScript) → `let/const`, Arrow Functions, Destructuring  
- [React](ca://s?q=ReactJS_c%C6%A1_b%E1%BA%A3n) → JSX, Components, Props  

**Thực hành:**  
- Xây dựng **Home Page** gồm:  
  - Header  
  - Banner  
  - FeatureSection  
  - Footer  

**Kết quả:**  
- Một trang chủ cơ bản, giao diện đơn giản nhưng đầy đủ.  
- Sinh viên hiểu rõ cách xây dựng UI bằng **React Components** và truyền dữ liệu qua **Props**.  

**Tài liệu tham khảo:**  
- [React Official Docs](https://react.dev/learn)  
- [W3Schools React](https://www.w3schools.com/React/)  

# ✨ Tuần 2 – Bắt đầu lên kế hoạch và phát triển sản phẩm

# 🚀 Session 03 – Product Catalog 15/06/2026

## 🎯 Objective
Hiển thị danh sách sản phẩm.

---

## 📚 Theory
- **Component Reusability**  
- **Props/State**  
- **Array Mapping**  
- **React Hooks**: `useState`, `useEffect`, `useContext`  

---

## 🛠️ Hands-on Practice
Tạo các component:
- **ProductCard**  
- **ProductList**  

Sử dụng mock data:
- **products.json**

---

## ✅ Outcome
Danh mục sản phẩm được hiển thị dưới dạng **card format**.

# ✨ Tuần 3 – Quản lý trạng thái & Điều hướng ứng dụng

## 🚀 Session 04 – Search & Filter (19/06/2026)

### 🎯 Objective
Quản lý **application state**.

### 📚 Theory
- **React Hooks (cont.)**  
- **Data handling & Axios GET**  
- **Layout** với CSS, Bootstrap, Tailwind, CSS Modules  

### 🛠️ Hands-on Practice
- **Product Search**  
- **Category Filtering**  
- **Price Sorting**  

### ✅ Outcome
Catalog sản phẩm **tương tác** với khả năng lọc và sắp xếp.

---

## 🚀 Session 05 – Multi-Page Application (22/06/2026)

### 🎯 Objective
Triển khai **application navigation**.

### 📚 Theory
- **React Router**  
- **Route**  
- **Navigate**  
- **Route Parameters**  

### 🛠️ Hands-on Practice
Tạo các trang:
- `/`  
- `/products`  
- `/products/:id`  
- `/cart`  
- `/login`  

### ✅ Outcome
Ứng dụng có **page navigation** đầy đủ.

---

## 🚀 Session 06 – FastAPI Product API (25/06/2026)

### 🎯 Objective
Xây dựng **backend API** đầu tiên.

### 📚 Theory
- **FastAPI**  
- **RESTful APIs**  
- **GET / POST / PUT / DELETE**  
- **Swagger Documentation**  

### 🛠️ Hands-on Practice
Triển khai các endpoint:
- `GET /products`  
- `GET /products/{id}`  
- `POST /products`  
- `PUT /products/{id}`  
- `DELETE /products/{id}`  

### ✅ Outcome
API sản phẩm chạy và được **documented via Swagger**.

---

## 🚀 Session 07 – Integrating React with APIs (26/06/2026)

### 🎯 Objective
Thay thế mock data bằng **real API data**.

### 📚 Theory
- **Axios**  
- **HTTP Requests**  
- **Async/Await**  

### 🛠️ Hands-on Practice
Tiêu thụ API:
- `GET /products`  
- `GET /products/{id}`  

### ✅ Outcome
Frontend lấy dữ liệu trực tiếp từ **backend API**.
