import client from "./client";

export interface User {
  serial: number;
  user_id: string;
  username: string;
  email: string;
  role: string;
  status: string;
  created_at: string;
}

export async function getUsers(): Promise<User[]> {
  const { data } = await client.get<{ users: User[]; total: number }>("/users/");
  return data.users;
}

export async function createUser(payload: {
  user_id: string;
  username: string;
  password: string;
  role: string;
  email?: string;
}): Promise<void> {
  await client.post("/users/", payload);
}

export async function deleteUser(userId: string): Promise<void> {
  await client.delete(`/users/${userId}`);
}
