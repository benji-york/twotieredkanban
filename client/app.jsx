import React from 'react';
import ReactDOM from 'react-dom';
import {Route, Router, IndexRoute, hashHistory} from 'react-router';

import Site from './ui/site';
import {Board} from './ui/board';

require('./styles/app.scss');

class Main extends React.Component {
  render() {
    return (
      <div>
        {this.props.children}
      </div>
      );
  }
}

ReactDOM.render(
<Router history={hashHistory}>
  <Route path="/" component={Main}>
    <IndexRoute component={Site} />
    <Route path="board/:name" component={Board} />
  </Route>
</Router>,
document.getElementById('app')
);
