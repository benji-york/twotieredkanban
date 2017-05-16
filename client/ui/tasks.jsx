import React from 'react';
import {Card, CardText} from 'react-toolbox';

import {Dialog, DialogBase, Input} from './dialog';
import {Draggable, DropZone} from './dnd';

class TaskDialog extends DialogBase {
  
  render() {
    const action = this.action();
    
    return (
      <Dialog title={action + " task"} action={action} ref="dialog"
              finish={() => this.finish(this.state)}>
        <Input label='Title' required={true} onChange={this.val("title")} />
        <Input label='Description' multiline={true}
               onChange={this.val("description")} />
        <Input label='Size' type="number" required={true}
               onChange={this.val("size", 1)} />
        <Input label='Blocked' multiline={true}
               onChange={this.val("blocked")} />
      </Dialog>
    );
  }
}

class AddTask extends TaskDialog {

  action() { return "Add"; }

  finish(data) {
    this.props.api.add_task(
      this.props.project.id, data.title, data.description,
      data.size, data.blocked);
  }  
}

class EditTask extends TaskDialog {

  action() { return "Edit"; }

  show() {
    const task = this.props.task;
    super.show({id: task.id,
                title: task.title,
                description: task.description,
                size: task.size,
                blocked: task.blocked
               });
  }

  finish(data) {
    this.props.api.update_task(data.id, data.title, data.description,
                               parseInt(data.size), data.blocked);
  }
}


class TaskBoard extends React.Component {

  render() {

    const {project} = this.props;

    const headers = () => {
      return project.state.substates.map((state) => {
        return <th key={state.id}>{state.title}</th>;
      });
    };

    const columns = () => {
      return project.state.substates.map((state) => {
        return (
          <td key={state.id}>
            <TaskColumn
               project={project}
               state={state}
               tasks={project.subtasks(state.id)}
               api={this.props.api}
               />
          </td>
        );
      });
    };

    return (
      <div className="kb-task-board">
        <table>
          <thead><tr>{headers()}</tr></thead>
          <tbody><tr>{columns()}</tr></tbody>
        </table>
      </div>
    ); 
  }
}

class TaskColumn extends React.Component {

  dropped(dt, before_id) {
    this.props.api.move(
      dt.getData('text/id'), // id of task to be moved
      this.props.project.id, // id of destination project
      this.props.state.id,   // destination state id
      before_id);            // move before task with before_id (optional)
    console.log(before_id, dt.getData('text/id'));
  } 

  tasks() {
    return this.props.tasks.map((task) => {

      const dropped = (dt) => this.dropped(dt, task.id); 

      return (
        <div key={task.id}>
          <DropZone className="kb-divider" dropped={dropped} />
          <Draggable data={{'text/id': task.id}}>
            <Task task={task} api={this.props.api} />
          </Draggable>
        </div>
      );
    });
  }

  render() {

    const dropped = (dt) => this.dropped(dt); 

    return (
      <div className="kb-column">
        {this.tasks()}
        <DropZone className="kb-divider kb-tail" dropped={dropped} />
      </div>
    );

  }

}

class Task extends React.Component {

  shouldComponentUpdate(nextProps, nextState) {
    return (nextProps.task.rev !== this.rev);
  }

  size() {
    return this.props.task.size > 1 ? '[' + this.props.task.size + ']' : '';
  }
  
  render() {
    this.rev = this.props.task.rev;

    return (
      <Card onClick={() => this.refs.edit.show()}>
        <CardText>
          {this.props.task.title} {this.size()}
        </CardText>
        <EditTask ref="edit" task={this.props.task} api={this.props.api} />
      </Card>
    );
  }
}

module.exports = {
  AddTask: AddTask,
  Task: Task,
  TaskBoard: TaskBoard
};
