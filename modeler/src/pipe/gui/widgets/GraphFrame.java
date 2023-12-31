package pipe.gui.widgets;

import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Window;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import javax.swing.ImageIcon;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JTextArea;
import net.sourceforge.jpowergraph.defaults.DefaultGraph;
import net.sourceforge.jpowergraph.defaults.TextEdge;
import net.sourceforge.jpowergraph.layout.Layouter;
import net.sourceforge.jpowergraph.layout.spring.SpringLayoutStrategy;
import net.sourceforge.jpowergraph.lens.CursorLens;
import net.sourceforge.jpowergraph.lens.LegendLens;
import net.sourceforge.jpowergraph.lens.LensSet;
import net.sourceforge.jpowergraph.lens.NodeSizeLens;
import net.sourceforge.jpowergraph.lens.RotateLens;
import net.sourceforge.jpowergraph.lens.TooltipLens;
import net.sourceforge.jpowergraph.lens.TranslateLens;
import net.sourceforge.jpowergraph.lens.ZoomLens;
import net.sourceforge.jpowergraph.manipulator.dragging.DraggingManipulator;
import net.sourceforge.jpowergraph.manipulator.popup.PopupManipulator;
import net.sourceforge.jpowergraph.painters.edge.LineEdgePainter;
import net.sourceforge.jpowergraph.painters.edge.LoopEdgePainter;
import net.sourceforge.jpowergraph.swing.SwingJGraphPane;
import net.sourceforge.jpowergraph.swing.SwingJGraphScrollPane;
import net.sourceforge.jpowergraph.swing.SwingJGraphViewPane;
import net.sourceforge.jpowergraph.swing.manipulator.SwingPopupDisplayer;
import net.sourceforge.jpowergraph.swtswinginteraction.color.JPowerGraphColor;
import pipe.gui.CreateGui;
import pipe.jpowergraph.RGGeneralState;
import pipe.jpowergraph.RGInitialState;
import pipe.jpowergraph.RGLineWithTextEdgePainter;
import pipe.jpowergraph.RGLoopWithTextEdge;
import pipe.jpowergraph.RGLoopWithTextEdgePainter;
import pipe.jpowergraph.RGNode;
import pipe.jpowergraph.RGSwingContextMenuListener;
import pipe.jpowergraph.RGSwingToolTipListener;


/**
 * @author Moqi
 * 该类用于显示RG.
 */
@SuppressWarnings("serial")
public class GraphFrame extends JFrame {
   
   SwingJGraphPane jGraphPane;
   DefaultGraph graph = null;
   JPanel panel = null;
   
   public void constructGraphFrame(DefaultGraph graph, String rgLegend) {
	   
      this.setIconImage(new ImageIcon(CreateGui.imgPath + "icon.png").getImage());
      this.graph = graph;

      setSize(800, 600);
      setLocation(100, 100);
      
      addWindowListener(new WindowAdapter() {
         public void windowClosing(WindowEvent wev) {
            Window w = wev.getWindow();
            w.setVisible(false);
            w.dispose();
         }
      });
      
      jGraphPane = new SwingJGraphPane(graph);
      Font font = new Font("PingFang SC", Font.PLAIN, 10);
      jGraphPane.setFont(font);
      
      LensSet lensSet = new LensSet();
      lensSet.addLens(new RotateLens());
      lensSet.addLens(new TranslateLens());
      lensSet.addLens(new ZoomLens());
      
      CursorLens m_draggingLens = new CursorLens();      
      lensSet.addLens(m_draggingLens);
      
      lensSet.addLens(new TooltipLens());
      lensSet.addLens(new LegendLens());
      lensSet.addLens(new NodeSizeLens());

      jGraphPane.setLens(lensSet);         
      
      
      jGraphPane.addManipulator(new DraggingManipulator(m_draggingLens, -1));
      jGraphPane.addManipulator(new PopupManipulator(jGraphPane, 
                (TooltipLens) lensSet.getFirstLensOfType(TooltipLens.class)));
      
      jGraphPane.setNodePainter(RGGeneralState.class, 
              RGGeneralState.getShapeNodePainter());      

      jGraphPane.setNodePainter(RGInitialState.class, 
              RGInitialState.getShapeNodePainter());            
      
      jGraphPane.setDefaultNodePainter(RGNode.getShapeNodePainter());
      
      jGraphPane.setEdgePainter(TextEdge.class, 
              new RGLineWithTextEdgePainter(JPowerGraphColor.BLACK, 
              JPowerGraphColor.GRAY, false));
      
      jGraphPane.setDefaultEdgePainter(new LineEdgePainter(JPowerGraphColor.BLACK, 
              JPowerGraphColor.GRAY, false));
      
      jGraphPane.setEdgePainter(RGLoopWithTextEdge.class, 
              new RGLoopWithTextEdgePainter(JPowerGraphColor.GRAY, 
              JPowerGraphColor.GRAY, LoopEdgePainter.RECTANGULAR));
      
      jGraphPane.setAntialias(true);
      
      jGraphPane.setPopupDisplayer(new SwingPopupDisplayer(new RGSwingToolTipListener(), 
              new RGSwingContextMenuListener(graph, new LensSet(), new Integer[]{}, new Integer[]{})));

      Layouter m_layouter = new Layouter(new SpringLayoutStrategy(graph));
      m_layouter.start();
      
      SwingJGraphScrollPane scroll = new SwingJGraphScrollPane(jGraphPane, lensSet);

      SwingJGraphViewPane view = new SwingJGraphViewPane(scroll, lensSet, true);

    
      GridBagLayout gbl = new GridBagLayout();
      GridBagConstraints gbc = new GridBagConstraints();
      gbc.gridwidth = GridBagConstraints.REMAINDER;
      gbc.fill = GridBagConstraints.HORIZONTAL;
      gbc.anchor = GridBagConstraints.NORTHWEST;
      panel = new JPanel();
      panel.setLayout(gbl);
      getContentPane().add("Center", view);
      getContentPane().add("West", panel);
      
      
      JTextArea legend = new JTextArea(rgLegend);
      legend.setFont(font);
      legend.setEditable(false);
      
      getContentPane().add("South", legend);
      
      setVisible(true);      
   }
   
}