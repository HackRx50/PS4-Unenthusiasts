todo_list = []
current_id = 1  


def add_todo_item(item: str) -> str:
    global current_id
    todo_id = current_id
    todo_list.append({"item_id": todo_id, "item": item})
    current_id += 1  
    return f"Added to-do item: {item} with ID: {todo_id}"


def list_todo_items() -> str:
    if not todo_list:
        return "Your to-do list is empty."
    return "Your to-do items are:\n" + "\n".join([f"{todo['item_id']}: {todo['item']}" for todo in todo_list])


def update_todo_item(item_id: int,new_item:str) -> str:
    
    
    todo_id = item_id
    new_item = new_item

    for todo in todo_list:
        if todo["item_id"] == todo_id:
            todo["item"] = new_item
            return f"Updated to-do item with ID: {todo_id} to: {new_item}"
    return f"No to-do item found with ID: {todo_id}"


def delete_todo_item(todo_id: int) -> str:
    global todo_list
    todo_list = [todo for todo in todo_list if todo["item_id"] != todo_id]
    return f"Deleted to-do item with ID: {todo_id}"

