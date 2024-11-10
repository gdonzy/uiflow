export interface ListItem {
    id: number;
    name: string;
    description: string;
    createdAt: string;
}
  
export interface ListResponse {
    items: ListItem[];
    total: number;
}
  