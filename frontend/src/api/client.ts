import axios from "axios";

// /**
//  * Todo の型定義
//  */
// export interface Todo {
//   id: number;
//   title: string;
//   content: string;
//   created_at: Date;
//   updated_at: Date;
// }

// /**
//  * Todo 作成時のリクエスト
//  */
// export interface TodoCreateRequest {
//   title: string;
//   content: string;
// }

// /**
//  * Todo 更新時のリクエスト
//  */
// export interface TodoUpdateRequest {
//   title: string;
//   content: string;
// }

// /**
//  * Todo のレスポンス
//  */
// export interface TodoResponse {
//   id: number;
//   title: string;
//   content: string;
//   created_at: string;
//   updated_at: string;
// }

// /**
//  * JSON で受け付けた API のレスポンスを扱いやすい型定義に変換する
//  * @param raw
//  */
// function toTodo(res: TodoResponse): Todo {
//   return {
//     ...res,
//     created_at: new Date(res.created_at),
//     updated_at: new Date(res.updated_at),
//   };
// }

export const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

// /**
//  * Todo 一覧取得
//  * @returns
//  */
// export async function todoList(): Promise<Todo[]> {
//   const { data } = await api.get("/todos");
//   return data.map(toTodo);
// }

// /**
//  * Todo 1件取得
//  * @param id
//  * @returns
//  */
// export async function todoDetail(id: number): Promise<Todo> {
//   const { data } = await api.get(`/todos/${id}`);
//   return toTodo(data);
// }

// /**
//  * Todo 新規作成
//  * @param body
//  * @returns
//  */
// export async function todoAdd(body: TodoCreateRequest): Promise<Todo> {
//   const { data } = await api.post("/todos", body);
//   return toTodo(data);
// }

// /**
//  * Todo 更新
//  * @param body
//  * @returns
//  */
// export async function todoUpdate(
//   id: number,
//   body: TodoUpdateRequest,
// ): Promise<Todo> {
//   const { data } = await api.patch(`/todos/${id}`, body);
//   return toTodo(data);
// }

// /**
//  * Todo 削除
//  * @param id
//  */
// export async function todoDelete(id: number): Promise<void> {
//   await api.delete(`/todos/${id}`);
// }
